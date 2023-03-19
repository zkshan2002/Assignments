#include "sysinclude.h"
#include <stdio.h>
#include <deque>

extern void SendFRAMEPacket(unsigned char *pData, unsigned int len);

#define WINDOW_SIZE_STOP_WAIT 1
#define WINDOW_SIZE_BACK_N_FRAME 4

typedef enum {
    data,
    ack,
    nak,
} FrameType;
struct FrameHead {
    FrameType type;
    unsigned int sendID;
    unsigned int ackID;
    unsigned char data[100];
};
struct Frame {
    FrameHead head;
    unsigned int size;
};
struct Data {
    void *p;
    unsigned int size;
};

// store data that have not been either acknowledged or sent yet
static deque <Data> sendBuffer;
static unsigned int notAckCnt;
static unsigned int windowSize;

static void sendPackets() {
    for (int i = notAckCnt; i < sendBuffer.size() && i < windowSize; i++) {
        Data *dataPtr = &(sendBuffer[i]);
        SendFRAMEPacket((unsigned char*)dataPtr->p, dataPtr->size);
        notAckCnt++;
        Frame *framePtr = (Frame*)(dataPtr->p);
        unsigned int sendID = ntohl((framePtr->head).sendID);
        printf("***Send %u, notAckCnt %u\n", sendID, notAckCnt);
    }
}

static int handleSendRequest(char *pBuffer, int bufferSize, UINT8 messageType) {
    // store data in buffer
    void *p = malloc(bufferSize);
    memcpy(p, pBuffer, bufferSize);
    Data data;
    data.p = p;
    data.size = bufferSize;
    sendBuffer.push_back(data);
    
    Frame *framePtr = (Frame *) (data.p);
    unsigned int sendID = ntohl((framePtr->head).sendID);
    printf("***----------Send request %u----------\n", sendID);
    sendPackets();
    return 0;
}

static void clearAcknowledgedPacket(int ackID) {
    // iterate buffer from beginning, clear data with sendID <= ackID
    while (!sendBuffer.empty()) {
        Frame *framePtr = (Frame *) (sendBuffer[0].p);
        unsigned int sendID = ntohl((framePtr->head).sendID);
        // ignore late ack msg
        if (ackID < sendID) {
            break;
        }
        // clear acknowledged data
        free(framePtr);
        sendBuffer.pop_front();
        notAckCnt--;
        printf("***Pop front sendID %u, notAckCnt %u\n", sendID, notAckCnt);
    }
}

static void resendAll() {
	printf("***Resend all\n");
    for (int i = 0; i < sendBuffer.size() && i < windowSize; i++) {
        Data *dataPtr = &(sendBuffer[i]);
        SendFRAMEPacket((unsigned char*)dataPtr->p, dataPtr->size);
        Frame *framePtr = (Frame*)(dataPtr->p);
        unsigned int sendID = ntohl((framePtr->head).sendID);
        printf("***Resend %u, notAckCnt %u\n", sendID, notAckCnt);
    }
}

static int stud_slide_window(char *pBuffer, int bufferSize, UINT8 messageType, int choice) {
    if (messageType == MSG_TYPE_SEND) {
        return handleSendRequest(pBuffer, bufferSize, messageType);
    } else if (messageType == MSG_TYPE_RECEIVE) {
    	Frame *framePtr = (Frame*)pBuffer;
        unsigned int ackID = ntohl((framePtr->head).ackID);
        printf("***----------Receive ackID %d----------\n", ackID);
        FrameType frameType = (FrameType)ntohl((framePtr->head).type);
        if (frameType == nak) {
            if (!choice) {
                return -1;
            }
            printf("***NAK. Resend all\n");
            resendAll();
            return 0;
        }
        clearAcknowledgedPacket(ackID);
        printf("***Cleared Ack packets. notAckCnt %d, sendBufferSize %llu \n", notAckCnt, sendBuffer.size());
        sendPackets();
    } else if (messageType == MSG_TYPE_TIMEOUT) {
        printf("***----------Timeout----------\n");
        resendAll();
    } else {
        return -1;
    }
    return 0;
}

/*
* 停等协议测试函数
*/
int stud_slide_window_stop_and_wait(char *pBuffer, int bufferSize, UINT8 messageType) {
    windowSize = WINDOW_SIZE_STOP_WAIT;
    return stud_slide_window(pBuffer, bufferSize, messageType, 0);
}

/*
* 回退n帧测试函数
*/
int stud_slide_window_back_n_frame(char *pBuffer, int bufferSize, UINT8 messageType) {
    windowSize = WINDOW_SIZE_BACK_N_FRAME;
    return stud_slide_window(pBuffer, bufferSize, messageType, 0);
}

/*
* 选择性重传测试函数
*/
int stud_slide_window_choice_frame_resend(char *pBuffer, int bufferSize, UINT8 messageType) {
    windowSize = WINDOW_SIZE_BACK_N_FRAME;
    return stud_slide_window(pBuffer, bufferSize, messageType, 1);
}