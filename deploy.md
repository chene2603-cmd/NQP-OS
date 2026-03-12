# NQP-OS v1.2 部署指南
## 适配平台
- x86_64 工业主机（Linux 4.18+ 内核）
- 国产ARM64硬件：RK3588/RK3568（Linux 5.10+ 内核，开启XDP功能）

## RK3588 交叉编译与部署步骤
### 1. 环境准备
- 交叉编译工具链：aarch64-linux-gnu-gcc/clang（版本10+）
- 依赖库：libbpf-dev (ARM64版本)、libxdp-dev (ARM64版本)
- 内核配置：开启CONFIG_XDP_SOCKETS、CONFIG_BPF_SYSCALL

### 2. eBPF 程序交叉编译
```bash
# 编译eBPF内核对象（ebpf_kern.o）
clang -target aarch64-linux-gnu -O2 -g -c ebpf_kern.c -o ebpf_kern.o -D__BPF__
# 编译用户态程序（ebpf_user）
aarch64-linux-gnu-gcc ebpf_user.c -o ebpf_user -lbpf -lxdp -lpthread