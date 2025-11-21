/*
 * AVX2-Optimized Spectral Analysis Functions
 * ===========================================
 *
 * High-performance implementations of common audio DSP operations
 * using AVX2 SIMD instructions.
 */

#include <Python.h>
#include <numpy/arrayobject.h>
#include <immintrin.h>
#include <math.h>
#include <string.h>

/* Check for AVX2 support at runtime */
static int check_avx2_support(void) {
    unsigned int eax, ebx, ecx, edx;

    /* Check if CPUID is supported */
    __asm__ __volatile__ (
        "cpuid"
        : "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
        : "a"(7), "c"(0)
    );

    /* Check AVX2 bit (bit 5 of EBX) */
    return (ebx & (1 << 5)) != 0;
}

/*
 * AVX2-optimized vector magnitude computation
 * Computes sqrt(real^2 + imag^2) for complex arrays
 */
static void magnitude_avx2(const float* real, const float* imag,
                           float* output, size_t n) {
    size_t i;
    const size_t avx2_width = 8;  /* Process 8 floats at a time */
    size_t n_vec = (n / avx2_width) * avx2_width;

    /* Vectorized loop */
    for (i = 0; i < n_vec; i += avx2_width) {
        __m256 r = _mm256_loadu_ps(&real[i]);
        __m256 im = _mm256_loadu_ps(&imag[i]);

        /* Compute r^2 + im^2 */
        __m256 r_sq = _mm256_mul_ps(r, r);
        __m256 im_sq = _mm256_mul_ps(im, im);
        __m256 sum = _mm256_add_ps(r_sq, im_sq);

        /* Compute sqrt */
        __m256 mag = _mm256_sqrt_ps(sum);

        _mm256_storeu_ps(&output[i], mag);
    }

    /* Handle remaining elements */
    for (; i < n; i++) {
        float r = real[i];
        float im = imag[i];
        output[i] = sqrtf(r*r + im*im);
    }
}

/*
 * Fallback non-AVX2 implementation
 */
static void magnitude_scalar(const float* real, const float* imag,
                             float* output, size_t n) {
    for (size_t i = 0; i < n; i++) {
        float r = real[i];
        float im = imag[i];
        output[i] = sqrtf(r*r + im*im);
    }
}

/*
 * AVX2-optimized power spectral density computation
 * Computes 20 * log10(magnitude)
 */
static void power_spectrum_avx2(const float* magnitude, float* output, size_t n) {
    size_t i;
    const size_t avx2_width = 8;
    size_t n_vec = (n / avx2_width) * avx2_width;

    const float log10_const = 20.0f / logf(10.0f);
    __m256 log_scale = _mm256_set1_ps(log10_const);
    __m256 epsilon = _mm256_set1_ps(1e-10f);  /* Avoid log(0) */

    /* Vectorized loop */
    for (i = 0; i < n_vec; i += avx2_width) {
        __m256 mag = _mm256_loadu_ps(&magnitude[i]);

        /* Add epsilon to avoid log(0) */
        mag = _mm256_add_ps(mag, epsilon);

        /* Compute natural log (no AVX2 log, use approximation or scalar) */
        /* For simplicity, we'll use a scalar fallback for log */
        float temp[8];
        _mm256_storeu_ps(temp, mag);

        for (int j = 0; j < 8; j++) {
            temp[j] = log10_const * logf(temp[j]);
        }

        __m256 result = _mm256_loadu_ps(temp);
        _mm256_storeu_ps(&output[i], result);
    }

    /* Handle remaining elements */
    for (; i < n; i++) {
        output[i] = 20.0f * log10f(magnitude[i] + 1e-10f);
    }
}

/*
 * AVX2-optimized mean computation
 */
static float mean_avx2(const float* data, size_t n) {
    size_t i;
    const size_t avx2_width = 8;
    size_t n_vec = (n / avx2_width) * avx2_width;

    __m256 sum_vec = _mm256_setzero_ps();

    /* Vectorized accumulation */
    for (i = 0; i < n_vec; i += avx2_width) {
        __m256 val = _mm256_loadu_ps(&data[i]);
        sum_vec = _mm256_add_ps(sum_vec, val);
    }

    /* Horizontal sum */
    float temp[8];
    _mm256_storeu_ps(temp, sum_vec);
    float sum = temp[0] + temp[1] + temp[2] + temp[3] +
                temp[4] + temp[5] + temp[6] + temp[7];

    /* Add remaining elements */
    for (; i < n; i++) {
        sum += data[i];
    }

    return sum / (float)n;
}

/*
 * AVX2-optimized variance computation
 */
static float variance_avx2(const float* data, size_t n, float mean) {
    size_t i;
    const size_t avx2_width = 8;
    size_t n_vec = (n / avx2_width) * avx2_width;

    __m256 mean_vec = _mm256_set1_ps(mean);
    __m256 sum_sq = _mm256_setzero_ps();

    /* Vectorized loop */
    for (i = 0; i < n_vec; i += avx2_width) {
        __m256 val = _mm256_loadu_ps(&data[i]);
        __m256 diff = _mm256_sub_ps(val, mean_vec);
        __m256 sq = _mm256_mul_ps(diff, diff);
        sum_sq = _mm256_add_ps(sum_sq, sq);
    }

    /* Horizontal sum */
    float temp[8];
    _mm256_storeu_ps(temp, sum_sq);
    float sum = temp[0] + temp[1] + temp[2] + temp[3] +
                temp[4] + temp[5] + temp[6] + temp[7];

    /* Add remaining elements */
    for (; i < n; i++) {
        float diff = data[i] - mean;
        sum += diff * diff;
    }

    return sum / (float)(n - 1);
}

/* ========== Python Interface Functions ========== */

/*
 * Python wrapper for magnitude computation
 */
static PyObject* py_magnitude(PyObject* self, PyObject* args) {
    PyArrayObject *real_array, *imag_array, *output_array;

    if (!PyArg_ParseTuple(args, "O!O!O!",
                         &PyArray_Type, &real_array,
                         &PyArray_Type, &imag_array,
                         &PyArray_Type, &output_array)) {
        return NULL;
    }

    /* Validate inputs */
    if (PyArray_TYPE(real_array) != NPY_FLOAT32 ||
        PyArray_TYPE(imag_array) != NPY_FLOAT32 ||
        PyArray_TYPE(output_array) != NPY_FLOAT32) {
        PyErr_SetString(PyExc_TypeError, "Arrays must be float32");
        return NULL;
    }

    npy_intp n = PyArray_SIZE(real_array);

    if (PyArray_SIZE(imag_array) != n || PyArray_SIZE(output_array) != n) {
        PyErr_SetString(PyExc_ValueError, "Array sizes must match");
        return NULL;
    }

    float* real = (float*)PyArray_DATA(real_array);
    float* imag = (float*)PyArray_DATA(imag_array);
    float* output = (float*)PyArray_DATA(output_array);

    /* Use AVX2 if supported, otherwise fallback */
    if (check_avx2_support()) {
        magnitude_avx2(real, imag, output, n);
    } else {
        magnitude_scalar(real, imag, output, n);
    }

    Py_RETURN_NONE;
}

/*
 * Python wrapper for power spectrum computation
 */
static PyObject* py_power_spectrum(PyObject* self, PyObject* args) {
    PyArrayObject *magnitude_array, *output_array;

    if (!PyArg_ParseTuple(args, "O!O!",
                         &PyArray_Type, &magnitude_array,
                         &PyArray_Type, &output_array)) {
        return NULL;
    }

    if (PyArray_TYPE(magnitude_array) != NPY_FLOAT32 ||
        PyArray_TYPE(output_array) != NPY_FLOAT32) {
        PyErr_SetString(PyExc_TypeError, "Arrays must be float32");
        return NULL;
    }

    npy_intp n = PyArray_SIZE(magnitude_array);

    if (PyArray_SIZE(output_array) != n) {
        PyErr_SetString(PyExc_ValueError, "Array sizes must match");
        return NULL;
    }

    float* magnitude = (float*)PyArray_DATA(magnitude_array);
    float* output = (float*)PyArray_DATA(output_array);

    if (check_avx2_support()) {
        power_spectrum_avx2(magnitude, output, n);
    } else {
        /* Scalar fallback */
        for (npy_intp i = 0; i < n; i++) {
            output[i] = 20.0f * log10f(magnitude[i] + 1e-10f);
        }
    }

    Py_RETURN_NONE;
}

/*
 * Python wrapper for mean computation
 */
static PyObject* py_mean(PyObject* self, PyObject* args) {
    PyArrayObject *data_array;

    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &data_array)) {
        return NULL;
    }

    if (PyArray_TYPE(data_array) != NPY_FLOAT32) {
        PyErr_SetString(PyExc_TypeError, "Array must be float32");
        return NULL;
    }

    npy_intp n = PyArray_SIZE(data_array);
    float* data = (float*)PyArray_DATA(data_array);

    float result = mean_avx2(data, n);

    return PyFloat_FromDouble((double)result);
}

/*
 * Python wrapper for variance computation
 */
static PyObject* py_variance(PyObject* self, PyObject* args) {
    PyArrayObject *data_array;
    float mean = 0.0f;
    int compute_mean = 1;

    if (!PyArg_ParseTuple(args, "O!|fi",
                         &PyArray_Type, &data_array,
                         &mean, &compute_mean)) {
        return NULL;
    }

    if (PyArray_TYPE(data_array) != NPY_FLOAT32) {
        PyErr_SetString(PyExc_TypeError, "Array must be float32");
        return NULL;
    }

    npy_intp n = PyArray_SIZE(data_array);
    float* data = (float*)PyArray_DATA(data_array);

    if (compute_mean) {
        mean = mean_avx2(data, n);
    }

    float result = variance_avx2(data, n, mean);

    return PyFloat_FromDouble((double)result);
}

/*
 * Check if AVX2 is available
 */
static PyObject* py_has_avx2(PyObject* self, PyObject* args) {
    if (check_avx2_support()) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

/* ========== Module Definition ========== */

static PyMethodDef module_methods[] = {
    {"magnitude", py_magnitude, METH_VARARGS,
     "Compute magnitude of complex array (AVX2-optimized)"},
    {"power_spectrum", py_power_spectrum, METH_VARARGS,
     "Compute power spectrum in dB (AVX2-optimized)"},
    {"mean", py_mean, METH_VARARGS,
     "Compute mean of array (AVX2-optimized)"},
    {"variance", py_variance, METH_VARARGS,
     "Compute variance of array (AVX2-optimized)"},
    {"has_avx2", py_has_avx2, METH_NOARGS,
     "Check if AVX2 is supported"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "avx2_spectral",
    "AVX2-optimized spectral analysis functions",
    -1,
    module_methods
};

PyMODINIT_FUNC PyInit_avx2_spectral(void) {
    import_array();  /* Initialize NumPy */
    return PyModule_Create(&module_def);
}
