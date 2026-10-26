# H3 Cloud MCP

用本机 MCP 工具调用 AutoDL Art 托管的 MiniMax H3 文生视频工作流。按生成秒计费，无需租 GPU、下载权重或维持实例。需要自控 ComfyUI 时，也保留通过 SSH 隧道连接私有实例的备用工具。仓库不含模型权重、令牌、私钥、素材或成片。

**方案选择**：[AutoDL Art 托管 H3 工作流](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v_no_pic)适合少量出片，是本仓库默认路线。[AutoDL Art 的 H3 社区应用](https://www.autodl.art/app/market/252)已带 H3 和工作流，适合需要控制节点、插件或批量任务的用户，但会产生 GPU 和系统盘费用。下方手动下载流程仅供需要独立环境时使用。

## 托管 API：先用这条路线

AutoDL Art 页面在 2026-10-26 标价：480p 高峰 08:00–24:00 为 ¥0.04/生成秒，低峰 00:00–08:00 为 ¥0.03/生成秒；768p 分别为 ¥0.05 与 ¥0.04。**默认 5 秒 480p 横屏，页面价格约 ¥0.15–0.20**。全部 H3 型号、任务类别、分辨率及 AutoDL Art 18 个工作流的对照见[完整价格矩阵](docs/h3-price-matrix.md)。价格会变动，提交前必须在[工作流页面](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v_no_pic)核对。代码里的限额只依据观察到的价格估算，无法代替平台实际计费上限。

1. 登录 AutoDL Art，在[令牌管理](https://autodl.art/large-model/tokens)创建分组为 **ComfyUI** 的令牌。新账户可能需要先自行完成实名认证。不要将令牌或身份资料写进仓库、MCP 配置文件或聊天记录。
2. 安装 Python 3.11+ 与 `uv`，执行 `uv sync`。在 MCP 进程的私有环境中提供 `AUTODL_ART_TOKEN`。先运行 `h3_art_quote`，核对平台实时价格与钱包余额。
3. 准备付费时才设置 `H3_ART_ENABLE_PAID=1`。默认还限制一次 MCP 进程只提交一条任务，并拒绝根据已观察高峰价格估算超过 ¥0.25 的调用。下例使用环境变量注入令牌；不要把真实令牌替换到文档或 shell 历史中。

```sh
uv sync
AUTODL_ART_TOKEN="$(security find-generic-password -s h3-cloud-mcp-autodl-art -w)" \
  H3_ART_ENABLE_PAID=1 \
  uv run h3-cloud-mcp
```

macOS 可先由用户自行将令牌存入钥匙串，服务名称 `h3-cloud-mcp-autodl-art`。其他系统用其秘密管理器向 MCP 进程提供环境变量。`H3_ART_MAX_ESTIMATED_CNY` 默认 `0.25`，`H3_ART_MAX_TASKS_PER_SESSION` 默认 `1`；只在确认平台报价与预算后调整。MCP **不会重试提交 POST**：请求超时可能代表任务已经创建，先查平台账单或任务列表，避免重复扣费。

macOS 用户把令牌存入钥匙串后，可在 MCP 客户端把 stdio 命令指向 [`scripts/run-art-mcp-macos.sh`](scripts/run-art-mcp-macos.sh)。脚本在启动时从钥匙串读取令牌，并保持每个进程最多一条、每条按已观察价格估算最多 ¥0.25。令牌过期或额度用完后，更新钥匙串令牌即可；不要把令牌放进客户端的明文配置。首次保存令牌时，在交互式终端执行 `security add-generic-password -a "$(id -un)" -s h3-cloud-mcp-autodl-art -w`，按提示输入令牌；已存在的条目加 `-U` 更新。不要把令牌写在命令行参数里。

Codex CLI 示例：

```sh
codex mcp add h3-art -- /absolute/path/h3-cloud-mcp/scripts/run-art-mcp-macos.sh
```

| 工具 | 作用 |
| --- | --- |
| `h3_art_quote` | 本地估算价格，不产生费用。 |
| `h3_art_generate` | 提交文生视频任务，返回 `task_id`，默认 5 秒 480p 横屏。 |
| `h3_art_job_status` | 查询任务状态，不显示临时签名下载地址。 |
| `h3_art_download_video` | 成功后立即下载 MP4 到 `H3_OUTPUT_DIR`（默认 `outputs/`）。 |

示例调用：`h3_art_generate({"prompt":"雨夜的街道，镜头缓慢向前推进，霓虹灯倒映在地面","duration":5,"resolution":"480p横"})`。拿到 `task_id` 后调用 `h3_art_job_status`，成功后调用 `h3_art_download_video`。下载地址有效期较短。托管服务的视频质量、声音与实际扣费要通过真实任务验收；本地模拟测试不等于已出片。

## 私有 ComfyUI 备用工具

- `h3_check_backend`：检查 ComfyUI 可达性、H3 节点和四个权重文件是否可见。
- `h3_generate`：提交文生音画任务，立即返回 `job_id`；默认 768×448、124 帧、20 步，约 5.17 秒。
- `h3_job_status`：查询排队、运行、完成或失败。
- `h3_download_video`：下载完成的 MP4 到本机 `outputs/`。
- `h3_cancel_job`：移除排队任务，或请求中断指定的运行任务。

私有 ComfyUI 工具只提供 FL2VA 文生音画。托管 API 工具只提供官方 H3 文生视频工作流。首尾帧、参考视频和导演台工作流尚未接入。未真实生成验收前，请把它们视为本地已测试的适配器。

## 选择算力

需要自己控制 ComfyUI 时，先核对 AutoDL Art 的现成 H3 应用及其 GPU 报价。若必须手动部署，再考虑按量计费的单张 RTX 5090 32GB，主机内存建议至少 64GB，数据盘留出至少 50GB 可用空间。按 2026-10-26 AutoDL.com 页面观察，5090 约 ¥2.93/小时原价；部分地区或会员价约 ¥2.78/小时。现货、镜像、磁盘费用必须在下单时重新核对。一次任务的总费用取决于模型下载、冷启动、排队、生成和实例开机时长，不能仅按采样秒数计算。按量实例开机到关机按秒计费，最低 ¥0.01，无需凑满一小时。关机后普通实例的数据保留，连续关机 15 天会释放；付费扩容磁盘即使关机仍可能计费。AutoDL Art 的应用系统盘另按日计费，关机也计费。

低价 vGPU-32GB 页面显示为 RTX 4080S，标价约 ¥1.66/小时；RTX 4090 24GB 约 ¥2.08/小时。它们都不是 Blackwell，这份 NVFP4 预设不支持；替换编码器与工作流后才能单独实测。价格与库存记录见 [调研记录](docs/cost-and-sources.md)。

## 云端准备（手动部署备用）

1. 在 AutoDL 选择单张 RTX 5090，选择可用的 ComfyUI 镜像，确认 GPU、内存、数据盘容量与小时价。不要开启付费扩容，除非已核对持续存储成本。
2. 在实例内运行 `nvidia-smi`，确认 GPU 可用。仓库提供 [`scripts/bootstrap-comfyui.sh`](scripts/bootstrap-comfyui.sh)，从官方 GitHub 固定提交安装 ComfyUI 及依赖，并检查现有 PyTorch 的 CUDA 和 `sm_120` 内核；若镜像自带可用的 ComfyUI，可跳过安装。云端需要原生 `MiniMaxH3ImageToVideo`、`VAEDecodeAudio`、`CreateVideo` 和 `SaveVideo` 节点。本次安装验证的版本为 0.42.0。

   ```sh
   bash scripts/bootstrap-comfyui.sh
   ```
3. 把下列四个文件放到 ComfyUI 对应 `models/` 子目录。优先把文件下载到 AutoDL 数据盘，再以符号链接挂载，避免 30GB 系统盘溢出。文件总计约 39.6 GiB；下载缓存、解压和输出仍需额外空间。文件来源为 [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)：

   | 目录 | 文件 |
   | --- | --- |
   | `diffusion_models` | `minimax_h3_fl2va_pruned_int8_convrot.safetensors` |
   | `text_encoders` | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
   | `vae` | `minimax_h3_video_vae_fp16.safetensors` |
   | `vae` | `minimax_h3_audio_vae_fp32.safetensors` |

   仓库提供 [`scripts/download-models.sh`](scripts/download-models.sh)。它用 `curl` 从固定模型提交下载四个必需文件，支持断点续传，并在建立软链接前逐个核对 SHA-256。官方 Hugging Face 不可达时，可设置 `H3_DOWNLOAD_ORIGIN=https://hf-mirror.com`；镜像只是下载来源，文件内容仍须通过校验。首次下载前检查磁盘余量与模型许可。

   ```sh
   H3_DOWNLOAD_ORIGIN=https://hf-mirror.com bash scripts/download-models.sh
   ```

4. 在云端启动 ComfyUI，只监听实例的 `127.0.0.1:8188`，输出写入数据盘；本机再建立隧道：

   ```sh
   mkdir -p /root/autodl-tmp/h3-outputs
   python /root/ComfyUI/main.py --listen 127.0.0.1 --port 8188 --output-directory /root/autodl-tmp/h3-outputs
   ```

   ```sh
   ssh -N -L 8188:127.0.0.1:8188 -p <AutoDL SSH 端口> root@<AutoDL SSH 地址>
   ```

5. 本机执行 `curl -fsS http://127.0.0.1:8188/system_stats`，确认连接。这一步不代表模型已生成成功。

AutoDL 的 [实例计费规则](https://www.autodl.com/docs/price/)以实例开关机时间计费，关机后付费扩容数据盘仍可能计费。模型许可、磁盘及实例的保留方式应在长期运行前确认。

## 私有 ComfyUI 的本机安装

需要 Python 3.11+、`uv` 和已建立的 SSH 隧道：

```sh
uv sync
COMFYUI_URL=http://127.0.0.1:8188 uv run h3-cloud-mcp
```

在 MCP 客户端中配置 stdio 命令（将路径替换为本机仓库绝对路径）：

```json
{
  "mcpServers": {
    "h3-cloud": {
      "command": "uv",
      "args": ["run", "--project", "/absolute/path/h3-cloud-mcp", "h3-cloud-mcp"],
      "env": {"COMFYUI_URL": "http://127.0.0.1:8188", "H3_OUTPUT_DIR": "/absolute/path/h3-cloud-mcp/outputs"}
    }
  }
}
```

示例调用：`h3_generate({"prompt":"夜晚的台北街头，镜头缓慢推进，雨滴落在霓虹灯下，环境声自然"})`，随后用返回的 `job_id` 调用 `h3_job_status` 与 `h3_download_video`。提交前先运行 `h3_check_backend`，确认 `h3_models_ready=true`。帧数须符合 `17n+5`，并处于模型标注的 124–362 帧训练范围；124 帧约 5.17 秒。若模型文件名不同，用 `H3_MODEL`、`H3_TEXT_ENCODER`、`H3_VIDEO_VAE`、`H3_AUDIO_VAE` 环境变量覆盖。

默认最多允许一个活动任务；需要并行时用 `H3_MAX_ACTIVE_JOBS=2` 等设置，上限为 4。超过默认 `768×448×124帧×20步` 计算量的请求会被拒绝；清楚核对费用后才设置 `H3_ALLOW_LARGE_JOBS=1`。这些限制只控制 MCP 提交，**不会替代 AutoDL 的关机计时器**。遇到作业卡住，可用 `h3_cancel_job`，再到 AutoDL 页面确认实例状态与消费。

## 安全与许可

MCP 限制 `COMFYUI_URL` 为本机 HTTP 地址，预期通过 SSH 隧道访问。不应将 ComfyUI 8188 端口或此 MCP 服务直接开放到公网。公开仓库仅授权本仓库代码（MIT）；MiniMax H3 权重由 [MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE) 单独约束。其许可排除美国、欧盟、英国、韩国等地区，且对向第三方开放生成服务设有额外要求；公开代码不等于可以向全球提供 H3 托管服务。部署和使用前自行核对当前许可文本。生成内容由使用者负责。

## 验证范围

托管 API 已在 2026-10-26 完成一次真实验收：检查价格和余额 → 使用限额令牌 → 提交一条任务 → 查询成功 → 下载 MP4 → 核对实际费用。产物是 5.167 秒、864×480 的 H.264/AAC 视频；详见[验收记录](docs/validation.md)。私有 ComfyUI 备用路线仍只通过本地模拟测试，未完成真实 GPU 出片验收。
