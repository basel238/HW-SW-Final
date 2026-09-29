/* Native CPU demonstration only. No RTL driver/custom instruction is present.
 * RMAG uses sqrt and is NOT bit-identical to nbody flat_pow.
 * Finite benchmark-like inputs only; no general exception fallback implemented.
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <math.h>
#include <stdlib.h>

/* ---- GEOM CPU ordered arithmetic helpers (ordered, per-op rounding, no FMA) ---- */
static inline double GEOM_VDOT3(double a0,double a1,double a2,
                                double b0,double b1,double b2){
    double m0=a0*b0, m1=a1*b1, m2=a2*b2;   /* 3 rounded multiplies */
    double s0=m0+m1;                        /* rounded add          */
    return s0+m2;                           /* rounded add -> result*/
}
static inline double GEOM_RMAG(double d2,double dt){
    double s = sqrt(d2);                     /* FSQRT */
    double dd = d2*s;                        /* FMUL  */
    return dt/dd;                            /* FDIV  -> dt/(d2*sqrt(d2)) */
}
/* returns 1 if a root exists (writes *dist), 0 for no-root */
static inline int GEOM_SPHERE(double cpx,double cpy,double cpz,
                              double dx,double dy,double dz,
                              double r,double *dist){
    double v  = GEOM_VDOT3(cpx,cpy,cpz, dx,dy,dz);
    double q  = GEOM_VDOT3(cpx,cpy,cpz, cpx,cpy,cpz);
    double disc = r*r - (q - v*v);
    if (disc < 0.0) return 0;
    *dist = v - sqrt(disc);
    return 1;
}

/* ------------------------------------------------------------------ helpers */
static int read_doubles(PyObject *seq, double *out, Py_ssize_t n){
    for (Py_ssize_t i=0;i<n;i++){
        PyObject *it = PySequence_GetItem(seq,i);
        if(!it) return -1;
        out[i] = PyFloat_AsDouble(it);
        Py_DECREF(it);
        if (out[i]==-1.0 && PyErr_Occurred()) return -1;
    }
    return 0;
}
static int write_doubles(PyObject *seq, const double *in, Py_ssize_t n){
    for (Py_ssize_t i=0;i<n;i++){
        PyObject *f = PyFloat_FromDouble(in[i]);
        if(!f) return -1;
        if (PySequence_SetItem(seq,i,f)<0){ Py_DECREF(f); return -1; }
        Py_DECREF(f);
    }
    return 0;
}

/* ------------------------------------------------ advance_nbody_approx(pos,vel,mass,dt,steps) */
static const int PAIRS[10][2] = {{0,1},{0,2},{0,3},{0,4},{1,2},
                                 {1,3},{1,4},{2,3},{2,4},{3,4}};

static PyObject* py_advance_nbody_approx(PyObject *self, PyObject *args){
    PyObject *pos_o,*vel_o,*mass_o; double dt; long steps;
    if(!PyArg_ParseTuple(args,"OOOdl",&pos_o,&vel_o,&mass_o,&dt,&steps))
        return NULL;
    double pos[15], vel[15], mass[5];
    if(read_doubles(pos_o,pos,15)<0) return NULL;
    if(read_doubles(vel_o,vel,15)<0) return NULL;
    if(read_doubles(mass_o,mass,5)<0) return NULL;

    Py_BEGIN_ALLOW_THREADS               /* pure numeric loop: release the GIL */
    for (long s=0;s<steps;s++){
        for (int p=0;p<10;p++){
            int i=PAIRS[p][0], j=PAIRS[p][1], bi=i*3, bj=j*3;
            double dx=pos[bi]-pos[bj], dy=pos[bi+1]-pos[bj+1], dz=pos[bi+2]-pos[bj+2];
            double d2  = GEOM_VDOT3(dx,dy,dz, dx,dy,dz);   /* CPU arithmetic control */
            double mag = GEOM_RMAG(d2, dt);                /* CPU arithmetic control */
            double mi=mass[i]*mag, mj=mass[j]*mag;
            vel[bi]-=dx*mj; vel[bi+1]-=dy*mj; vel[bi+2]-=dz*mj;
            vel[bj]+=dx*mi; vel[bj+1]+=dy*mi; vel[bj+2]+=dz*mi;
        }
        for (int k=0;k<5;k++){ int b=k*3;
            pos[b]+=dt*vel[b]; pos[b+1]+=dt*vel[b+1]; pos[b+2]+=dt*vel[b+2]; }
    }
    Py_END_ALLOW_THREADS

    if(write_doubles(pos_o,pos,15)<0) return NULL;
    if(write_doubles(vel_o,vel,15)<0) return NULL;
    Py_RETURN_NONE;
}

/* -------------------------------- intersect_scene(...) -> (dist, idx) */
static PyObject* py_intersect_scene(PyObject *self, PyObject *args){
    PyObject *centers_o,*radii_o;
    double ox,oy,oz,dx,dy,dz,eps;
    if(!PyArg_ParseTuple(args,"OOddddddd",&centers_o,&radii_o,
                         &ox,&oy,&oz,&dx,&dy,&dz,&eps)) return NULL;
    Py_ssize_t n = PySequence_Length(radii_o);
    if(n<0) return NULL;
    double *centers = (double*)malloc(sizeof(double)*3*n);
    double *radii   = (double*)malloc(sizeof(double)*n);
    if(!centers||!radii){ free(centers); free(radii);
        return PyErr_NoMemory(); }
    if(read_doubles(centers_o,centers,3*n)<0 || read_doubles(radii_o,radii,n)<0){
        free(centers); free(radii); return NULL; }

    double best=INFINITY; long best_i=-1;
    for (Py_ssize_t k=0;k<n;k++){
        double cpx=centers[3*k]-ox, cpy=centers[3*k+1]-oy, cpz=centers[3*k+2]-oz;
        double dist;
        if(GEOM_SPHERE(cpx,cpy,cpz, dx,dy,dz, radii[k], &dist)){  /* CPU arithmetic control */
            if(dist>eps && dist<best){ best=dist; best_i=k; }
        }
    }
    free(centers); free(radii);
    return Py_BuildValue("(dl)", best, best_i);
}

/* ------------------------------------------------------------------ module */
static PyMethodDef methods[] = {
    {"advance_nbody_approx",   py_advance_nbody_approx,   METH_VARARGS,
     "advance_nbody_approx(pos,vel,mass,dt,steps): in-place nbody integration"},
    {"intersect_scene", py_intersect_scene, METH_VARARGS,
     "intersect_scene(centers,radii,ox,oy,oz,dx,dy,dz,eps) -> (dist,idx)"},
    {NULL,NULL,0,NULL}
};
static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT, "_geomaccel_c",
    "Native GEOM FP64 microkernels (VDOT3/RMAG/SPHERE)", -1, methods
};
PyMODINIT_FUNC PyInit__geomaccel_c(void){ return PyModule_Create(&moduledef); }
