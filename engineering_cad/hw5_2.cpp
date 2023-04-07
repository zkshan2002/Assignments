#include <cstdio>
#include <array>
#include <list>

static FILE *fp;

struct point {
    double x, y, z;

    void print() const {
        fprintf(fp, "%g,%g,%g", x, y, z);
    }
};

void line(std::list<point> point_list) {
    fprintf(fp, "line");
    for (const auto &p: point_list) {
        fprintf(fp, " ");
        p.print();
    }
    fprintf(fp, " \n");
}

// draw a box that center at (x, y, z).
// draw cross at every surface except +x, -x
void box(double half_length, double x, double y, double z) {
    std::array<point, 8> pts;
    std::array<int, 4> bias1 = {1, -1, -1, 1};
    std::array<int, 4> bias2 = {1, 1, -1, -1};
    for (int i = 0; i < 8; i++) {
        double current_x = x + half_length * bias1[i % 4];
        double current_y = y + half_length * bias2[i % 4];
        double current_z = z + half_length * (i / 4 == 0 ? 1 : -1);
        pts[i] = {current_x, current_y, current_z};
    }
    line({pts[0], pts[1], pts[2], pts[3], pts[0]});
    line({pts[4], pts[5], pts[6], pts[7], pts[4]});
    for (int i = 0; i < 4; i++) {
        line({pts[i], pts[i + 4]});
    }
//   1---0
// 2---3 |
// | 5-+-4
// 6---7
    std::array<int, 8 * 2> indices = {0, 2, 1, 3, 2, 7, 3, 6, 0, 5, 1, 4, 4, 6, 5, 7};
    for (int i = 0; i < 8; i++) {
        line({pts[indices[i * 2]], pts[indices[i * 2 + 1]]});
    }
}

int main() {
    const auto file = "hw5_2.SCR";
    if ((fp = fopen(file, "w")) == nullptr) {
        printf("cannot open file %s", file);
        return 1;
    }
    double h;
    int n;
    scanf("%lf %d", &h, &n);
    if (h <= 0 || n <= 0) {
        printf("invalid parameters");
        return 1;
    }
    for (int i = 0; i < n; i++) {
        box(h / 2, h * i, 0, 0);
    }
    fclose(fp);
    return 0;
}