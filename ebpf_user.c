// eBPF内存管理修复：UMEM描述符循环复用机制
// edge_gateway/ebpf_user.c 核心代码

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <linux/if_xdp.h>
#include <bpf/libbpf.h>

#define XSK_RING_PROD__DEFAULT_NUM_DESCS 2048
#define XSK_UMEM__DEFAULT_FRAME_SIZE 4096

struct xsk_socket_info {
    struct xsk_socket *xsk;
    struct xsk_ring_prod tx;
    struct xsk_ring_cons rx;
    struct xsk_ring_prod fill;
    struct xsk_ring_cons comp;
    struct xsk_umem *umem;
    void *umem_area;
    __u32 umem_size;
};

static struct xsk_socket_info *xsk_configure(void *umem_area, __u32 umem_size,
                                             struct xsk_ring_prod *fill,
                                             struct xsk_ring_cons *comp) {
    struct xsk_socket_info *xsk_info = malloc(sizeof(*xsk_info));
    __u32 idx_fill;
    int ret;

    if (!xsk_info) {
        fprintf(stderr, "内存分配失败\n");
        return NULL;
    }

    xsk_info->umem_area = umem_area;
    xsk_info->umem_size = umem_size;

    // 初始化UMEM帧地址池：将所有帧地址放入fill队列
    ret = xsk_ring_prod__reserve(fill, XSK_RING_PROD__DEFAULT_NUM_DESCS, &idx_fill);
    if (ret != XSK_RING_PROD__DEFAULT_NUM_DESCS) {
        fprintf(stderr, "无法保留 fill 队列槽位\n");
        free(xsk_info);
        return NULL;
    }

    for (int i = 0; i < XSK_RING_PROD__DEFAULT_NUM_DESCS; i++) {
        *xsk_ring_prod__fill_addr(fill, idx_fill + i) = i * XSK_UMEM__DEFAULT_FRAME_SIZE;
    }
    xsk_ring_prod__submit(fill, XSK_RING_PROD__DEFAULT_NUM_DESCS);

    return xsk_info;
}

// 主处理循环：接收数据包+处理+归还UMEM帧地址
void xsk_main_loop(struct xsk_socket_info *xsk_info) {
    struct xdp_desc *desc;
    char *pkt;
    __u32 rcvd, i, idx_fill;
    int ret;

    while (1) {
        // 接收数据包
        rcvd = xsk_ring_cons__peek(&xsk_info->rx, 64, &i);
        if (!rcvd) continue;

        for (i = 0; i < rcvd; i++) {
            desc = xsk_ring_cons__rx_desc(&xsk_info->rx, i);
            pkt = xsk_info->umem_area + desc->addr;

            // 数据包处理逻辑（示例：可替换为实际业务）
            printf("接收数据包，长度：%d\n", desc->len);
            // process_packet(pkt, desc->len);

            // 处理完成后，归还帧地址到fill队列
            ret = xsk_ring_prod__reserve(&xsk_info->fill, 1, &idx_fill);
            if (ret == 1) {
                *xsk_ring_prod__fill_addr(&xsk_info->fill, idx_fill) = desc->addr;
                xsk_ring_prod__submit(&xsk_info->fill, 1);
            } else {
                // 应急：fill队列满时丢弃帧（实际场景极少发生）
                fprintf(stderr, "fill队列满，丢弃帧地址：%u\n", desc->addr);
            }
        }

        // 释放已处理的rx描述符
        xsk_ring_cons__release(&xsk_info->rx, rcvd);
    }
}

int main(int argc, char **argv) {
    // 示例主函数，实际使用需结合XSK初始化逻辑
    printf("eBPF UMEM帧回收机制已启用\n");
    return 0;
}