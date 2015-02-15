#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

#define TS_PACKET_SIZE 188
#define TRUE 1
#define FALSE 0

#define I_FRAME 2
#define P_FRAME 3
#define B_FRAME 4
#define DATA 5

//typedef enum {I_FRAME, P_FRAME, B_FRAME, NONE} h264_frame_t;
typedef unsigned Boolean; 
 
typedef unsigned char byte;

unsigned char TS_raw_header[4];
unsigned char TS_packet[TS_PACKET_SIZE];


struct NALHEADER
{
	byte  init[10];
	/*
	byte  nal_unit_type:5;			// Type - b00111 (07) : Sequence Parameter Set (SPS), b00001 (01) : non-IDR Slice without data partitioning
	byte  nal_ref_idc:2;			// NRI  - b11 : Highest, b10 : High, b01 : Low, b00 : Disposable
	byte  forbidden_zero_bit:1;
	*/
	unsigned char ref_num[2];
} NALHEADER;


struct SLICEHEADER
{
    byte  typeSlice;				// NRI b10 - 0x9A : P Frame (ref = 2), 0x9B : P Frame (ref = 2), 0x9E : B Frame (ref = 1), 0x9F : B Frame (ref = 1),
									// NRI b00 - 0x9E : B Frame (ref = 0), 0x9F : B Frame (ref = 0)
} SLICEHEADER;



struct TS_adaptation_field_header {
	unsigned char adaptation_field_length;
} TS_adaptation_field_header;

struct PES_header {
	unsigned char sync_bytes[3];
	unsigned char stream_id;
	unsigned char packet_length;
	unsigned char unused_bytes[14];
} PES_header;


struct TS_header
{
	unsigned char sync_byte;
	unsigned char transport_error_indicator;
	unsigned char payload_start_indicator;
	unsigned char transport_priority;
	unsigned int PID;
	unsigned char transport_scrambling_control;
	unsigned char adaption_field_control;
	unsigned char continuity_counter;
} TS_header;
 

unsigned remaining_bytes = 0;

 unsigned current_frame = FALSE;
 

Boolean PES_check_sanity(){
	if (PES_header.sync_bytes[0] == 0x00 &&
		PES_header.sync_bytes[1] == 0x00 &&
		PES_header.sync_bytes[2] == 0x01){
			return TRUE;
		}
	return FALSE;
}

unsigned PES_parse_packet(unsigned char offset){
	unsigned char o = offset;
	//printf("PES_header offset = %u\n", (unsigned)o);
	memcpy(&PES_header,TS_packet+o,sizeof(PES_header));
	//printf("here\n");
	if (!PES_check_sanity()) return FALSE;
	o = o + sizeof(PES_header);
	//printf("PES_payload offset = %u\n", (unsigned)o);
	memcpy(&NALHEADER,		TS_packet+o,						sizeof(NALHEADER));
	//memcpy(&SLICEHEADER,	TS_packet+o+sizeof(NALHEADER),		sizeof(SLICEHEADER));
	/*
	if(NALHEADER.nal_ref_idc == 3 && NALHEADER.nal_unit_type == 7) {
		current_frame = I_FRAME;
		printf("I frame header\n");
	//P or B frame header
	} else if(NALHEADER.nal_ref_idc == 2 && NALHEADER.nal_unit_type == 1) {
		// P frame header
		if (SLICEHEADER.typeSlice == 0x9A || SLICEHEADER.typeSlice == 0x9B){
			current_frame = P_FRAME;
			printf("P frame header\n");
		// B frame header with reference
		} else if (SLICEHEADER.typeSlice == 0x9E || SLICEHEADER.typeSlice == 0x9F){
			current_frame = B_FRAME;
			printf("B frame header\n");
		}
	//B frame header without reference
	} else if(NALHEADER.nal_ref_idc == 0 && NALHEADER.nal_unit_type == 1) {
		current_frame = B_FRAME;
		printf("B frame header\n");
	}*/
	if (NALHEADER.ref_num[0] == 0x41 && NALHEADER.ref_num[1] == 0x9A){
		current_frame = P_FRAME;
		//printf("P frame header\n");
	}else if (NALHEADER.ref_num[0] == 0x01 && NALHEADER.ref_num[1] == 0x9E){
		current_frame = P_FRAME;
		//printf("B frame header\n");
	}
	else {
		current_frame = I_FRAME;
		//printf("I frame header. refnum = %x %x \n",NALHEADER.ref_num[0],NALHEADER.ref_num[1]);
		
	}
	return current_frame;
}

void TS_header_decode()
{
	
	TS_header.sync_byte = TS_raw_header[0];
	TS_header.transport_error_indicator = (TS_raw_header[1] & 0x80) >> 7;
	TS_header.payload_start_indicator = (TS_raw_header[1] & 0x40) >> 6;
	TS_header.transport_priority = (TS_raw_header[1] & 0x20) >> 5;
	TS_header.PID = ((TS_raw_header[1] & 31) << 8) | TS_raw_header[2];
	TS_header.transport_scrambling_control = (TS_raw_header[3] & 0xC0);
	TS_header.adaption_field_control = (TS_raw_header[3] & 0x30) >> 4;
	TS_header.continuity_counter = (TS_raw_header[3] & 0xF);
}



// TODO: take care of remaining_bytes
unsigned TS_packet_classify(){
	unsigned res = -1;
	memcpy(TS_raw_header,TS_packet,sizeof(TS_raw_header));
	TS_header_decode();
	unsigned char offset = 0;
	if (TS_header.adaption_field_control == 1) { 
		//printf("payload only\n");
		offset = offset + sizeof(TS_raw_header);
		res = PES_parse_packet(offset);
		if (res == FALSE) return DATA;
		else return res;
		//else if (current_frame == I_FRAME) printf("I frame data\n");
		//else if (current_frame == P_FRAME) printf("P frame data\n");
		//else if (current_frame == B_FRAME) printf("B frame data\n");
		//else printf("unknown frame data\n");
	}
	else if (TS_header.adaption_field_control == 2) {
		//printf("adaptation field only\n");
		offset+=sizeof(TS_raw_header);
		memcpy(&TS_adaptation_field_header,TS_packet+offset,sizeof(TS_adaptation_field_header));
		res  = DATA;
		//printf("adaptation field size is %d bytes\n", TS_adaptation_field_header.adaptation_field_length);
	}
	else if (TS_header.adaption_field_control == 3) {
		//printf("adaptation field and payload\n");
		offset = offset + sizeof(TS_raw_header);
		//printf("TS_adaption payload offset = %u\n", (unsigned)offset);
		memcpy(&TS_adaptation_field_header,TS_packet+offset,sizeof(TS_adaptation_field_header));
		offset = offset + sizeof(TS_adaptation_field_header);
		//printf("TS_adaption payload offset = %u\n", (unsigned)offset);
		offset = offset + TS_adaptation_field_header.adaptation_field_length;
		//printf("here\n");
		res = PES_parse_packet(offset); 
		
	}
	
	return res;
}

unsigned ts_get_type(const char *ts_raw_data){
	assert( sizeof(ts_raw_data) == TS_PACKET_SIZE);
	memcpy(TS_packet,ts_raw_data,sizeof(ts_raw_data));
	return TS_packet_classify();
}

/*
int main(int argc, char** argv)
{
    char* filename = argv[1];
	unsigned int ts_packets = atoi(argv[2]);
    FILE *fp = fopen(filename,"rb");
    unsigned bytes_read;
	unsigned count = 1;
    while (!feof(fp) && count<ts_packets){
        bytes_read = fread(TS_packet, 1,TS_PACKET_SIZE, fp);
        assert(bytes_read == TS_PACKET_SIZE);
        memcpy(TS_raw_header,TS_packet,sizeof(TS_raw_header));
		printf("\n\nTS packet %u\n", count);
        TS_packet_print();
		count ++;
    }
    fclose(fp);
}
*/
