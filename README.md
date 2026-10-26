# H3 Cloud MCP

用本地 MCP 客户端调用 [AutoDL Art 的 MiniMax H3 文生视频工作流](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v_no_pic)：提交提示词、查询任务、下载 MP4。视频由 AutoDL Art 托管生成，使用者无需为这条路线单独租 GPU 或下载模型权重。

**当前状态：**文生视频链路已真实跑通两次。两条 5 秒、480p 横屏样片分别实扣 **¥0.20**，产物均为 864×480、5.167 秒的 H.264/AAC MP4。仓库已公开代码与[验收记录](docs/validation.md)；样片、令牌和个人资料不在仓库中。此 MCP 在你的电脑上以 stdio 运行，并不是已经部署好的公共在线服务。

> [完整使用说明书](docs/user-guide.md)：从注册／登录、实名认证、设置限额令牌，到安装、出片、核对账单和常见问题。首次使用请按说明书操作。

## 能做什么

| 已接通的托管工具 | 用途 |
| --- | --- |
| `h3_art_quote` | 按 2026-10-26 观察价格**本地估算**，不调用平台，不产生费用。 |
| `h3_art_generate` | 提交一条付费文生视频任务，返回 `task_id`。 |
| `h3_art_job_status` | 根据 `task_id` 查询排队、运行或完成状态。 |
| `h3_art_download_video` | 下载完成的 MP4 到本机 `outputs/`，或 `H3_OUTPUT_DIR` 指定的位置。 |

托管路线目前只接入工作流 `minimax_h3_lightx2v_no_pic`。支持 480p／768p 的横屏、竖屏或 1:1，时长 1–15 秒；默认 5 秒、480p 横屏。首尾帧、图生、多图参考等其他工作流目前**只做了价格调研，尚未接入 MCP**。[全部 H3 价格与类别](docs/h3-price-matrix.md)不等于本仓库已支持的功能。

## 五步开始（macOS）

1. 在 [AutoDL Art](https://autodl.art/) 登录；若平台要求，先完成实名认证。在[令牌管理](https://autodl.art/large-model/tokens)创建 **ComfyUI** 分组令牌，设置你能接受的总额度与短有效期。创建后检查页面显示的实际额度。
2. 安装 Python 3.11+、[`uv`](https://docs.astral.sh/uv/)；克隆仓库并安装依赖：

   ```sh
   git clone https://github.com/lst016/h3-cloud-mcp.git
   cd h3-cloud-mcp
   uv sync
   ```
3. 在你自己的交互式终端中，将令牌存入 macOS 钥匙串：

   ```sh
   security add-generic-password -U -a "$(id -un)" -s h3-cloud-mcp-autodl-art -w
   ```

   命令会提示输入令牌；不要把令牌写进命令参数、MCP 配置或 Git。其他操作系统可用自己的秘密管理器向 MCP 进程提供 `AUTODL_ART_TOKEN`。
4. 在仓库目录运行下列命令，把脚本的**绝对路径**注册到 Codex CLI；其他 MCP 客户端配置为同一个 stdio 命令。

   ```sh
   codex mcp add h3-art -- /absolute/path/h3-cloud-mcp/scripts/run-art-mcp-macos.sh
   ```

5. 打开[工作流价格页](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v_no_pic)核对实时单价，再在 MCP 客户端依次调用 `h3_art_quote` → `h3_art_generate` → `h3_art_job_status` → `h3_art_download_video`。示例：`h3_art_generate({"prompt":"一只透明玻璃鲸鱼在桌面上方缓慢游动，单镜头，无文字","duration":5,"resolution":"480p横"})`。

完整参数、Codex 配置、Windows／Linux 说明和出错处理见[使用说明书](docs/user-guide.md)。`scripts/run-art-mcp-macos.sh` 会启用付费提交，并在**每个 MCP 进程**中限制最多 1 条任务、按已观察高峰价估算最多 ¥0.25。这个本地估算不是平台账单上限；平台令牌额度要单独设置。提交超时后先查平台任务与账单，**不要盲目重复提交**。

## 成本：5 秒输出示例

| 路线与分辨率 | 单价 | 5 秒输出费用 | 证据 |
| --- | ---: | ---: | --- |
| AutoDL Art 托管工作流，480p 高峰 | ¥0.04/秒 | **¥0.20** | 两条真实样片分别实扣 ¥0.20 |
| AutoDL Art 托管工作流，480p 空闲 | ¥0.03/秒 | ¥0.15 | 页面报价，未在空闲时段实测 |
| AutoDL Art 托管工作流，768p 高峰／空闲 | ¥0.05／¥0.04 每秒 | ¥0.25／¥0.20 | 页面报价，未实测 |
| MiniMax 官方 H3-Lite API，480P | $0.025/秒 | 约 ¥0.84 | 官方目录价换算，未实测 |
| MiniMax 官方 H3 API，768P | $0.08/秒 | 约 ¥2.69 | 官方目录价换算，未实测 |

2026-10-26 汇率按 [100 美元 = ¥671.62](https://www.safe.gov.cn/AppStructured/hlw/RMBQuery.do)换算；[MiniMax 官方定价](https://platform.minimax.io/docs/pricing/overview)的输入视频和超额图片可能另收费。**不同型号与工作流的画质、排队和处理过程没有做同条件对照**。所有模型、分辨率、素材附加费和 AutoDL Art 18 个工作流的报价见[价格矩阵](docs/h3-price-matrix.md)。价格会变动，付费前以平台当前页面和账户预算为准。

## 文档与边界

- [使用说明书](docs/user-guide.md)：账户准备、令牌、安装、完整调用流程、成本和故障处理。
- [价格矩阵](docs/h3-price-matrix.md)：官方 H3 全型号与 AutoDL Art 18 个工作流。
- [验收记录](docs/validation.md)：两条真实出片与费用证据。
- [私有 ComfyUI 备用路线](docs/private-comfyui.md)：需自行租 GPU，当前只通过本地模拟测试，**未完成真实出片验收**。

公开仓库的 MIT 许可只覆盖本仓库代码。MiniMax H3 权重另受 [MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE) 约束；自行部署模型或向第三方提供服务前，应核对现行许可与使用地区。不要公开 API 令牌、签名下载地址或未经同意的素材。
