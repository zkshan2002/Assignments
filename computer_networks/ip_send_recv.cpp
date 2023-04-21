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
static unsigned short checksum(char *pBuffer, int length) {
    unsigned short *pBuffer_word = reinterpret_cast<unsigned short *>(pBuffer);
    unsigned int sum = 0;
    for (int i = 0; i < length; i++) {
        sum += pBuffer_word[i];
        sum = (sum >> 16) + (sum & 0xffff);
    }
    return ~static_cast<unsigned short>(sum);
}

int stud_ip_recv(char *pBuffer, unsigned short length) {
    unsigned char version = pBuffer[0] >> 4;
    if (version != 4) {
        ip_DiscardPkt(pBuffer, STUD_IP_TEST_VERSION_ERROR);
        return -1;
    }
    unsigned char head_length = pBuffer[0] & 0xf;
    if (head_length <= 4) {
        ip_DiscardPkt(pBuffer, STUD_IP_TEST_HEADLEN_ERROR);
        return -1;
    }
    unsigned char ttl = pBuffer[8];
    if (ttl <= 0) {
        ip_DiscardPkt(pBuffer, STUD_IP_TEST_TTL_ERROR);
        return -1;
    }
    unsigned short header_checksum = *reinterpret_cast<unsigned short *>(pBuffer + 10);
    if (checksum(pBuffer, head_length * 2)) {
        ip_DiscardPkt(pBuffer, STUD_IP_TEST_CHECKSUM_ERROR);
        return -1;
    }
    unsigned int dst_addr = ntohl(*reinterpret_cast<unsigned int *>(pBuffer + 16));
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
    *p = (4 << 4) | 5;
    *(p + 1) = 0;//TOS
    *reinterpret_cast<unsigned short *>(p + 2) = htons(length);
    *reinterpret_cast<unsigned short *>(p + 4) = 0;//sign
    *reinterpret_cast<unsigned short *>(p + 6) = 0;//flag+bias
    *(p + 8) = ttl;
    *(p + 9) = protocol;
    *reinterpret_cast<unsigned short *>(p + 10) = 0;
    *reinterpret_cast<unsigned int *>(p + 12) = htonl(srcAddr);
    *reinterpret_cast<unsigned int *>(p + 16) = htonl(dstAddr);
    *reinterpret_cast<unsigned short *>(p + 10) = checksum(p, 10);
    ip_SendtoLower(p, length);
    return 0;
}
