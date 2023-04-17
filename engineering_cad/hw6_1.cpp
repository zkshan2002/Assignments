#include <iostream>
#include <cmath>

struct cartesian {
    double x, y;
    double z = 0;

    cartesian operator+(const cartesian &rhs) const {
        return {this->x + rhs.x, this->y + rhs.y, this->z + rhs.z};
    }
};

struct polar {
    double deg, rou;

    operator cartesian() {
        double rad = this->deg / 180 * M_PI;
        return {this->rou * cos(rad), this->rou * sin(rad)};
    }
};

class DXFWriter {
private:
    FILE *fp;
public:
    DXFWriter(const char *file) {
        this->fp = fopen(file, "w");
        if (this->fp == nullptr) {
            printf("cannot open file %s", file);
            exit(1);
        }
        fprintf(this->fp, "0\nSECTION\n");
        fprintf(this->fp, "2\nENTITIES\n");
    }

    ~DXFWriter() {
        fprintf(this->fp, "0\nENDSEC\n");
        fprintf(this->fp, "0\nEOF");
        fclose(this->fp);
    }

    void add_line(const cartesian &src, const cartesian &dst, bool relative = false, int color = 0, int layer = 0) {
        fprintf(this->fp, "0\nLINE\n");
        fprintf(this->fp, "8\n%d\n", layer);
        if (color != 0) {
            fprintf(this->fp, "62\n%d\n", color);
        }
        fprintf(this->fp, "10\n%g\n", src.x);
        fprintf(this->fp, "20\n%g\n", src.y);
        if (src.z != 0) {
            fprintf(this->fp, "30\n%g\n", src.z);
        }
        cartesian dst2 = dst;
        if (relative) {
            dst2 = src + dst;
        }
        fprintf(this->fp, "11\n%g\n", dst2.x);
        fprintf(this->fp, "21\n%g\n", dst2.y);
        if (dst2.z != 0) {
            fprintf(this->fp, "31\n%g\n", dst2.z);
        }
    }

    void add_circle(const cartesian &center, double radius, int color = 0, int layer = 0) {
        fprintf(this->fp, "0\nCIRCLE\n");
        fprintf(this->fp, "8\n%d\n", layer);
        if (color != 0) {
            fprintf(this->fp, "62\n%d\n", color);
        }
        fprintf(this->fp, "10\n%g\n", center.x);
        fprintf(this->fp, "20\n%g\n", center.y);
        if (center.z != 0) {
            fprintf(this->fp, "30\n%g\n", center.z);
        }
        fprintf(this->fp, "40\n%g\n", radius);
    }

};


double ratio2deg(double ratio) {
    return 90.0 - ratio * 360;
}

int main() {
    auto g = DXFWriter("hw6_1.DXF");

    double R;
    int hour, min;
    scanf("%lf %d %d", &R, &hour, &min);

    g.add_line({0, 0}, polar{ratio2deg((hour + min / 60.0) / 12.0), R * 0.4}, false, 3);
    g.add_line({0, 0}, polar{ratio2deg(min / 60.0), R * 0.6}, false, 3);

    g.add_circle({0, 0}, R, 1);
    for (int i = 0; i < 12; i++) {
        double deg = ratio2deg(i / 12.0);
        g.add_line(polar{deg, R}, polar{deg, R * 0.8}, false, 1);
    }
    return 0;
}