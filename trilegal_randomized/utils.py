import numpy as np
import astropy.units as u

__all__ = ["RandomSkyPositions"]


class RandomSkyPositions:

    def __init__(self, ra0, dec0, radius, npts=None, seed=None):
        self.AA = np.matrix([[np.cos(ra0), -np.sin(ra0), 0],
                             [np.sin(ra0),  np.cos(ra0), 0],
                             [0, 0, 1]])
        self.BB = np.matrix([[-np.sin(dec0), 0, np.cos(dec0)],
                             [0, 1, 0],
                             [ np.cos(dec0), 0, np.sin(dec0)]])  # noqa: E201
        self.radius = radius
        self.npts = npts
        self.rng = np.random.Generator(np.random.PCG64(seed))
        self.zz = np.matrix([[0], [0], [1]])

    def __iter__(self):
        self.count = 0
        return self

    def __next__(self):
        if self.npts is not None and self.count >= self.npts:
            raise StopIteration
        self.count += 1
        theta = np.arccos(1.0 - self.rng.uniform()*(1 - np.cos(self.radius)))
        phi = 2.0*np.pi*self.rng.uniform()*u.radian
        CC = np.matrix([[np.cos(phi), -np.sin(phi), 0],  # noqa: N806
                        [np.sin(phi),  np.cos(phi), 0],
                        [0, 0, 1]])
        DD = np.matrix([[ np.cos(theta), 0, np.sin(theta)],  # noqa: E201, N806
                        [0, 1, 0],
                        [-np.sin(theta), 0, np.cos(theta)]])
        rr = self.AA @ self.BB @ CC @ DD @ self.zz
        ra = np.arctan2(rr[1, 0], rr[0, 0])*180./np.pi
        dec = np.arcsin(rr[2, 0])*180./np.pi
        return float(ra), float(dec)

    @staticmethod
    def make_generator(region, npts=None, seed=None):
        disk = region._get_bounding_disk()
        ra0 = disk.ra*u.degree
        dec0 = disk.dec*u.degree
        radius = disk.radius
        return RandomSkyPositions(ra0, dec0, radius, npts=npts, seed=seed)
