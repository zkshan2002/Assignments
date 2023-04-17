#include <iostream>
#include <cstring>
#include <vector>
#include <string>
#include <cmath>


class DXFParser {
private:
    FILE *fp;

    std::vector<std::string> read_lines() {
        char buffer[1024];
        std::vector<std::string> lines;
        while (fgets(buffer, sizeof(buffer), this->fp) != nullptr) {
            size_t len = strlen(buffer);
            if (len > 0 && buffer[len - 1] == '\n') {
                buffer[len - 1] = '\0';
            }
            lines.push_back(buffer);
        }
        fclose(this->fp);
        return lines;
    }

    std::vector<std::string> lines2entities(const std::vector<std::string> &lines) {
        std::vector<std::string> entities;
        int idx = 0;
        while (idx < lines.size()) {
            if (lines[idx++] == "ENTITIES") {
                break;
            }
        }
        while (lines[idx++] == "0") {
            if (lines[idx] == "ENDSEC") {
                break;
            }
            std::string entity = "0\n" + lines[idx] + "\n";
            idx++;
            while (lines[idx] != "0") {
                for (int i = 0; i < 2; i++) {
                    entity += lines[idx++] + "\n";
                }
            }
            entities.emplace_back(entity);
        }
        return entities;
    }

public:
    DXFParser(const char *file) {
        this->fp = fopen(file, "r");
        if (this->fp == nullptr) {
            printf("cannot open file %s", file);
            exit(1);
        }
    }

    ~DXFParser() {
        fclose(this->fp);
    }

    std::vector<std::string> parse() {
        return lines2entities(read_lines());
    }
};

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

    void add_entity(const std::string &entity) {
        fprintf(this->fp, "%s", entity.c_str());
    }

};

double ratio2deg(double ratio) {
    return 90.0 - ratio * 360;
}

int main() {
    auto parser = DXFParser("hw6_1.DXF");
    auto entities = parser.parse();

    auto writer = DXFWriter("hw6_2.DXF");

    auto circle_string = entities[2];
    size_t value_pos = circle_string.find("40") + 3;
    size_t end_pos = circle_string.find('\n', value_pos);
    std::string value = circle_string.substr(value_pos, end_pos - value_pos);
    double R = std::stod(value);

    int hour, min;
    scanf("%d %d", &hour, &min);

    writer.add_line({0, 0}, polar{ratio2deg((hour + min / 60.0) / 12.0), R * 0.4}, false, 3);
    writer.add_line({0, 0}, polar{ratio2deg(min / 60.0), R * 0.6}, false, 3);

    for (int i = 2; i < entities.size(); i++) {
        writer.add_entity(entities[i]);
    }

    return 0;
}