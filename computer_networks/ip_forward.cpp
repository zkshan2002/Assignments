/*
* THIS FILE IS FOR IP FORWARD TEST
*/
#include "sysInclude.h"

// system support
extern void fwd_LocalRcv(char *pBuffer, int length);

extern void fwd_SendtoLower(char *pBuffer, int length, unsigned int nexthop);

extern void fwd_DiscardPkt(char *pBuffer, int type);

extern unsigned int getIpv4Address();

// implemented by students
#include <vector>

static unsigned char read_byte(char *p) {
    return *p;
}

static unsigned char write_byte(char *p, unsigned char value) {
    *p = value;
}

static unsigned short read_word(char *p) {
    return ntohs(*reinterpret_cast<unsigned short *>(p));
}

static void write_word(char *p, unsigned short value) {
    *reinterpret_cast<unsigned short *>(p) = htons(value);
}

static unsigned int read_dword(char *p) {
    return ntohl(*reinterpret_cast<unsigned int *>(p));
}


static void write_dword(char *p, unsigned int value) {
    *reinterpret_cast<unsigned short *>(p) = htonl(value);
}

static std::vector<stud_route_msg> routing_table;

static unsigned short checksum(char *p, int length) {
    unsigned short *p_word = reinterpret_cast<unsigned short *>(p);
    unsigned int sum = 0;
    for (int i = 0; i < length; i++) {
        sum += htons(p_word[i]);
        sum = (sum >> 16) + (sum & 0xffff);
    }
    return ~static_cast<unsigned short>(sum);
}

void stud_Route_Init() {
    routing_table.clear();
}

void stud_route_add(stud_route_msg *proute) {
    routing_table.push_back(*proute);
}

int stud_fwd_deal(char *pBuffer, int length) {
    // If dstAddr is localAddr, receive
    unsigned int dst_addr = read_dword(pBuffer + 16);
    if (dst_addr == getIpv4Address() || dst_addr == 0xffffffff) {
        fwd_LocalRcv(pBuffer, length);
        return 0;
    }
    // else. If ttl <= 0, discard
    unsigned char ttl = read_byte(pBuffer + 8);
    if (ttl <= 0) {
        fwd_DiscardPkt(pBuffer, STUD_FORWARD_TEST_TTLERROR);
        return 1;
    }
    // else. Search the routing table for next hop.
    int max_len = 0, index = -1;
    for (int i = 0; i < routing_table.size(); i++) {
        unsigned int item_dst = ntohl(routing_table[i].dest);
        unsigned int mask_len = ntohl(routing_table[i].masklen);
        unsigned int mask = 0xffffffff << (32 - mask_len);
        // Match condition: higher mask_len bit matches
        // Among all matching items, pick the one with the largest mask_len. Pick the first to break ties.
        if (!((dst_addr ^ item_dst) & mask)) {
            if (max_len < mask_len) {
                max_len = mask_len;
                index = i;
            }
        }
    }
    // If all items do not match, discard
    if (index == -1) {
        fwd_DiscardPkt(pBuffer, STUD_FORWARD_TEST_NOROUTE);
        return 1;
    }
    // else. Update ttl, checksum, and send to lower layer.
    write_byte(pBuffer + 8, ttl - 1);
    write_word(pBuffer + 10, 0);
    write_word(pBuffer + 10, checksum(pBuffer, 10));
    // unsigned int header_length = read_byte(pBuffer) & 0xff;
    // unsigned short header_checksum = checksum(pBuffer, header_length * 2);
    // write_word(pBuffer + 10, header_checksum);
    fwd_SendtoLower(pBuffer, length, routing_table[index].nexthop);
    return 0;
}
