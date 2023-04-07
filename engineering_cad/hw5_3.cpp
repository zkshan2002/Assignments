#include <cstdio>

int main() {
    FILE *fp;
    const auto file = "hw5_3.SCR";
    if ((fp = fopen(file, "w")) == nullptr) {
        printf("cannot open file %s", file);
        return 1;
    }

    fprintf(fp, "-pan 0,0 2500,1500\n");
    fprintf(fp, "circle 0,0 100\n");
    for (int i = 0; i < 12; i++) {
        fprintf(fp, "line 100<%d @20<%d \n", i * 30, i * 30 + 180);
    }

    fprintf(fp, "line 0,0 @40<150 \n");
    fprintf(fp, "-group c hour  l \n");
    fprintf(fp, "line 0,0 @60<90 \n");
    fprintf(fp, "-group c min  l \n");
    fprintf(fp, "line 0,0 @70<90 \n");
    fprintf(fp, "-group c sec  l \n");
    fprintf(fp, "-text -50,-50 20 0 10:0:00 \n");

    for (int i = 1; i < 300; i++) {
        fprintf(fp, "delay 400\n");
        fprintf(fp, "erase l \n");
        fprintf(fp, "rotate g hour  0,0 %g\n", -6.0f / 60 / 60);
        fprintf(fp, "rotate g min  0,0 %g\n", -6.0f / 60);
        fprintf(fp, "rotate g sec  0,0 %g\n", -6.0f);
        fprintf(fp, "-text -50,-50 20 0 10:%02d:%02d \n", i / 60, i % 60);
    }

    fclose(fp);
    return 0;
}