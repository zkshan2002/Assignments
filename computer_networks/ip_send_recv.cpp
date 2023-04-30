/*
* THIS FILE IS FOR IP TEST
*/
// system support
#include "sysInclude.h"

extern void ip_DiscardPkt(char *pBuffer, int type);

extern void ip_SendtoLower(char *pBuffer, int length);

extern void ip_SendtoUp(char *pBuffer, int length);

extern unsigned int getIpv4Address();

// implemented by students
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

static unsigned short checksum(char *pBuffer, int length) {
    unsigned short *pBuffer_word = reinterpret_cast<unsigned short *>(pBuffer);
    unsigned int sum = 0;
    for (int i = 0; i < length; i++) {
        sum += htons(pBuffer_word[i]);
        sum = (sum >> 16) + (sum & 0xffff);
    }
    return ~static_cast<unsigned short>(sum);
}

int stud_ip_recv(char *pBuffer, unsigned short length) {
    unsigned char first_byte = read_byte(pBuffer);
    unsigned char version = first_byte >> 4;
    if (version != 4) {
        ip_DiscardPkt(pBuffer, STUD_IP_TEST_VERSION_ERROR);
        return -1;
    }
    unsigned char head_length = first_byte & 0xf;
    if (head_length <= 4) {
        ip_DiscardPkt(pBuffer, STUD_IP_TEST_HEADLEN_ERROR);
        return -1;
    }
    unsigned char ttl = read_byte(pBuffer + 8);
    if (ttl <= 0) {
        ip_DiscardPkt(pBuffer, STUD_IP_TEST_TTL_ERROR);
        return -1;
    }
    unsigned short header_checksum = read_word(pBuffer + 10);
    if (checksum(pBuffer, head_length * 2)) {
        ip_DiscardPkt(pBuffer, STUD_IP_TEST_CHECKSUM_ERROR);
        return -1;
    }
    unsigned int dst_addr = read_dword(pBuffer + 16);
    if (dst_addr != getIpv4Address() && dst_addr != 0xffffffff) {
        ip_DiscardPkt(pBuffer, STUD_IP_TEST_DESTINATION_ERROR);
        return -1;
    }
    ip_SendtoUp(pBuffer + 20, length - 20);
    return 0;
}

int stud_ip_Upsend(char *pBuffer, unsigned short len, unsigned int srcAddr,
                   unsigned int dstAddr, char protocol, char ttl) {
    unsigned short length = len + 20;
    char *p = reinterpret_cast<char *>(malloc(length));
    memcpy(p + 20, pBuffer, len);
    write_byte(p, (4 << 4) | 5);
    write_byte(p + 1, 0);//TOS
    write_word(p + 2, length);
    write_word(p + 4, 0);//sign
    write_word(p + 6, 0);//flag+bias
    write_byte(p + 8, ttl);
    write_byte(p + 9, protocol);
    write_word(p + 10, 0);
    write_dword(p + 12, srcAddr);
    write_dword(p + 16, dstAddr);
    write_word(p + 10, checksum(p, 10));
    ip_SendtoLower(p, length);
    return 0;
}
