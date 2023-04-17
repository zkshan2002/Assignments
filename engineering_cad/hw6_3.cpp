#include <iostream>
#include <cstring>
#include <vector>
#include <map>
#include <string>

struct cartesian {
    double x, y;
    double z = 0;

    cartesian operator+(const cartesian &rhs) const {
        return {this->x + rhs.x, this->y + rhs.y, this->z + rhs.z};
    }
};

struct geometric_entity {
public:
    std::string type;
    std::vector<cartesian> points;
    std::map<int, std::string> dict;
};

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

    std::vector<geometric_entity> lines2entities(const std::vector<std::string> &lines) {
        std::vector<geometric_entity> entities;
        int idx = 0;
        while (idx < lines.size()) {
            if (lines[idx++] == "ENTITIES") {
                break;
            }
        }
        while (true) {
            idx++;
            if (lines[idx] == "ENDSEC") {
                break;
            }
            geometric_entity entity;
            entity.type = lines[idx];
            idx++;
            while (true) {
                int key = atoi(lines[idx].c_str());
                if (key == 0) {
                    break;
                } else {
                    if (key == 10 || key == 11) {
                        double x = std::stod(lines[idx + 1]);
                        double y = std::stod(lines[idx + 3]);
                        idx += 4;
                        key = std::stod(lines[idx]);
                        cartesian point = {x, y};
                        if (key == 30 || key == 31) {
                            double z = std::stod(lines[idx + 1]);
                            idx += 2;
                            point.z = z;
                        }
                        entity.points.emplace_back(point);
                    } else {
                        entity.dict[atoi(lines[idx].c_str())] = lines[idx + 1];
                        idx += 2;
                    }
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

    std::vector<geometric_entity> parse() {
        return lines2entities(read_lines());
    }
};

class SCRWriter {
private:
    FILE *fp;
public:
    SCRWriter(const char *file) {
        this->fp = fopen(file, "w");
        if (this->fp == nullptr) {
            printf("cannot open file %s", file);
            exit(1);
        }
    }

    ~SCRWriter() {
        fclose(this->fp);
    }

    void add_command(const char *cmd) {
        fprintf(this->fp, "%s\n", cmd);
    }
};


int main() {
    auto parser = DXFParser("in.DXF");
    auto entities = parser.parse();
    auto writer = SCRWriter("hw6_3.SCR");
    for (auto &entity: entities) {
        auto type = entity.type;
        char buffer[1024];
        if (type == "POINT") {
            auto [x, y, z] = entity.points[0];
            sprintf(buffer, "point %g,%g,%g", x, y, z);
        } else if (type == "LINE") {
            auto [x, y, z] = entity.points[0];
            auto [x1, y1, z1] = entity.points[1];
            sprintf(buffer, "line %g,%g,%g %g,%g,%g ", x, y, z, x1, y1, z1);
        } else if (type == "CIRCLE") {
            auto [x, y, z] = entity.points[0];
            double radius = std::stod(entity.dict[40]);
            sprintf(buffer, "circle %g,%g,%g %g", x, y, z, radius);
        } else if (type == "ARC") {
            auto [x, y, z] = entity.points[0];
            double radius = std::stod(entity.dict[40]);
            double start_angle = std::stod(entity.dict[50]);
            double end_angle = std::stod(entity.dict[51]);
            sprintf(buffer, "arc c %g,%g @%g<%g %g", x, y, radius, start_angle, end_angle);
        } else if (type == "LWPOLYLINE") {
            buffer[0] = '\0';
            strcat(buffer, "polyline ");
            char buffer_s[64];
            for (const auto &p: entity.points) {
                auto [x, y, z] = p;
                sprintf(buffer_s, "%g,%g ", x, y);
                strcat(buffer, buffer_s);
            }
        } else {
            continue;
        }
        writer.add_command(buffer);
    }
    return 0;
}