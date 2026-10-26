# H3 Cloud MCP 使用说明书

更新：2026-10-26。本文带你从创建 AutoDL Art 账户走到使用 MiniMax H3 托管工作流生成、下载视频。MCP 服务在本机运行，生成任务由 AutoDL Art 执行，无需创建 GPU 实例。仓库地址：[lst016/h3-cloud-mcp](https://github.com/lst016/h3-cloud-mcp)。

**先看结果边界：**本项目已按平台输入表接入 18 个 H3 工作流。已真实出片的只有文生工作流：两条 480p、请求 5 秒的样片分别实扣 ¥0.20，MP4 均为 864×480、5.167 秒。其他类别完成本地参数与协议验证，尚未逐个付费出片；图片、音频需提供可访问的 HTTPS URL。[验收记录](validation.md)与[全部价格矩阵](h3-price-matrix.md)分别记录实测和报价。

## 1. 准备账户

1. 打开 [AutoDL Art](https://autodl.art/)。已有 AutoDL 账户，可在登录弹窗中选择 **“已登录 AutoDL，点击快速登录”**；新用户可按页面提供的注册、短信或微信入口完成账户创建。页面会因账户状态变化，按实际显示操作即可。
2. 登录后进入[令牌管理](https://autodl.art/large-model/tokens)。如果页面要求实名认证，先在平台内自行完成；涉及证件信息，不要交给 MCP、写进仓库或发给其他人。认证完成后刷新页面再创建令牌。首次登录若出现用户名设置，按页面完成；未出现就直接继续。
3. 确认账户有足够余额；余额不足时按平台页面提示先小额充值。对一次 5 秒 480p 文生视频，2026-10-26 页面高峰价为 ¥0.20、空闲价为 ¥0.15。充值、令牌额度与每次任务消费是不同概念，创建令牌不会生成视频。

## 2. 创建并保存 ComfyUI 令牌

1. 在[令牌管理](https://autodl.art/large-model/tokens)点击“创建新令牌”。名称可填 `h3-cloud-mcp`，**分组必须选 `ComfyUI`**；设置平台允许且符合自己预算的总消费额度、较短的有效期。提交后再次检查页面上**实际显示**的额度、状态与过期时间，不要只相信输入框里原先填的数字。
2. 复制令牌后仅保存在本机秘密管理器。令牌可在平台额度内提交付费任务，不能写入 README、`.env`、MCP 配置、聊天记录、截图或公开 Git 历史。
3. macOS 用户在自己的交互式终端执行以下命令；它会提示输入令牌，不把令牌放进命令行参数。再次运行会更新同名钥匙串条目：

   ```sh
   security add-generic-password -U -a "$(id -un)" -s h3-cloud-mcp-autodl-art -w
   ```

   Windows／Linux 用户用本机秘密管理器向 MCP 进程提供 `AUTODL_ART_TOKEN`，不要把真实值写进仓库中的配置示例。

令牌到期、撤销或额度耗尽后，在 AutoDL Art 创建或更新令牌，再更新本机秘密管理器。仓库不保存可用令牌，也不会替使用者长期续期。

## 3. 安装本地 MCP

需要 Python 3.11+、Git 与 [`uv`](https://docs.astral.sh/uv/)。macOS 示例：

```sh
git clone https://github.com/lst016/h3-cloud-mcp.git
cd h3-cloud-mcp
uv sync
```

将下面的路径换成你本机仓库的**绝对路径**，注册 stdio MCP 服务：

```sh
codex mcp add h3-art -- /absolute/path/h3-cloud-mcp/scripts/run-art-mcp-macos.sh
```

其他支持 MCP 的客户端也可把同一个脚本作为 `command`。例如常见的 MCP 配置形状如下；此处**没有明文令牌**：

```json
{
  "mcpServers": {
    "h3-art": {
      "command": "/absolute/path/h3-cloud-mcp/scripts/run-art-mcp-macos.sh"
    }
  }
}
```

脚本从 macOS 钥匙串读取令牌，设置 `H3_ART_ENABLE_PAID=1`，默认限制每个 MCP 进程最多提交 **1 条**任务、按当日已观察高峰价估算单条最多 **¥0.25**。首次出片后，若确实要生成下一条，须重启 MCP 进程；先核对新任务报价和平台余额。更高分辨率／更长视频若超过默认阈值，需先核对平台预算，再在启动前设置 `H3_ART_MAX_ESTIMATED_CNY`。这是**本地估算阈值，不是实际账单硬上限**，所以仍需设置平台令牌总额度。

Windows／Linux 可通过自己的秘密管理器启动 `uv run --project /absolute/path/h3-cloud-mcp h3-cloud-mcp`，并向该进程提供 `AUTODL_ART_TOKEN`、`H3_ART_ENABLE_PAID=1`；默认本地单条估算上限 ¥0.25、每进程 1 条。不要通过命令行参数或公开配置直接传入令牌。

## 4. 出一条视频

**先看实时价格：**打开所选工作流的[价格页](h3-price-matrix.md#autodl-art全部-h3-工作流及标价分辨率)，确认当前单价与时段。`h3_art_quote` 和 `h3_art_quote_workflow` 只把代码中 2026-10-26 的观察价相乘，**不读取平台实时价格、余额或令牌剩余额度**；二者不一致时以平台页面为准，暂停付费提交并更新配置。

在 MCP 客户端依次调用下列工具（这里的 JSON 是工具参数，不是终端命令）：

| 顺序 | 工具与示例参数 | 你应看到的结果 |
| --- | --- | --- |
| 1 | `h3_art_quote({"duration":5,"resolution":"480p横"})` | 本地估算价和已观察高峰价；不会扣费。 |
| 2 | `h3_art_generate({"prompt":"一只透明玻璃鲸鱼在桌面上方缓慢游动，单镜头，无文字","duration":5,"resolution":"480p横"})` | 提交一条付费任务，返回 `task_id`。 |
| 3 | `h3_art_job_status({"task_id":"上一步返回的 UUID"})` | `QUEUED`、`RUNNING` 或 `SUCCESS`；仍在运行就稍后用**同一个** `task_id` 查询。 |
| 4 | `h3_art_download_video({"task_id":"同一个 UUID"})` | 任务成功后下载 MP4，返回本机文件路径。 |

上表的快捷工具固定使用 `minimax_h3_lightx2v_no_pic`。它允许 `480p横`、`480p竖`、`480p(1:1)`、`768p横`、`768p竖`、`768p(1:1)`；`duration` 为 1–15 秒整数，默认 5 秒、480p 横屏。其他类别使用下节的 `h3_art_generate_workflow`。默认视频目录是仓库内 `outputs/`（已被 `.gitignore` 忽略），可用 `H3_OUTPUT_DIR` 改到其他本机目录。完成后尽快下载：平台返回的签名视频链接有效期有限。

`h3_art_job_status` 返回的 `processing_seconds` 来自平台任务字段，表示处理耗时，**不是 MP4 播放时长**；真实时长以下载后播放器或 `ffprobe` 为准。本项目两条请求 5 秒的样片实长均为 5.167 秒。

### 首尾帧、图生与音频参考

先调用 `h3_art_list_workflows({})` 查看每个工作流的分辨率、最长时长、图片和音频数量要求。再用 `h3_art_quote_workflow` 估价。例如 `h3_art_quote_workflow({"workflow_id":"minimax_h3_lightx2v","duration":5,"resolution":"480p横"})`。实际提交前，仍要打开该工作流页面核对实时价格。`workflow_id` 的全部 18 个可选值见[工作流价格矩阵](h3-price-matrix.md#autodl-art全部-h3-工作流及标价分辨率)。

下面是**参数示例，不是本仓库已经付费跑通的案例**。将 `.example` 地址换成平台能够读取的真实公开 HTTPS 素材地址；不要在公开文档中放带访问签名或私人资料的 URL。

```json
{"workflow_id":"minimax_h3_lightx2v","prompt":"一只玻璃鲸鱼缓慢游动","duration":5,"resolution":"480p横","first_frame":"https://images.example/first.png","last_frame":"https://images.example/last.png"}
```

上面的 JSON 是 `h3_art_generate_workflow` 的首尾帧参数。多图参考可改用 `minimax_h3_lightx2v_v5`，提供 `images` 数组：

```json
{"workflow_id":"minimax_h3_lightx2v_v5","prompt":"镜头平稳移动","duration":5,"resolution":"480p横","images":["https://images.example/one.png","https://images.example/two.png"]}
```

图音同步工作流使用一张图和一段音频，不接受 `prompt`；本工具会把 `duration` 转成平台要求的 `audio_duration`：

```json
{"workflow_id":"minimax_h3_image_audio_to_video","duration":5,"resolution":"480p横","images":["https://images.example/portrait.png"],"audios":["https://audio.example/voice.mp3"]}
```

以上三种任务提交后，都用返回的 `task_id` 调用同一组 `h3_art_job_status` 和 `h3_art_download_video`。`images`、`audios`、`first_frame`、`last_frame` 目前只接受公开 HTTPS URL；本机文件上传、base64 素材和输入视频尚未接入。所需素材数、时长、画幅因工作流而异，工具会在提交前检查；`minimax_h3_801`、`802`、`803` 另可传 `mode`（`高速模式` 或 `高质模式`）。高于默认 ¥0.25 本地估算阈值的任务会被拒绝，调整方法见第 3 节。

## 5. 核对费用，再考虑下一条

在 AutoDL Art 的令牌管理或调用日志查看任务后的累计消费。首次实测一条 5 秒 480p 高峰任务实扣 ¥0.20；第二次从累计 ¥0.20 增到 ¥0.40，仍是单条 ¥0.20。不要把页面报价或 MCP 的 `estimated_cny` 当作已经发生的账单。若打算公开展示，视频文件在本机；仓库只公开代码与验收记录，不自动上传视频，也不会替你发帖。

### 成本对比：5 秒输出

| 服务 / 模型 | 分辨率 | 页面或官方单价 | 5 秒输出费用 | 证据 |
| --- | --- | ---: | ---: | --- |
| AutoDL Art 本 MCP 工作流，高峰 | 480p | ¥0.040/秒 | **¥0.20** | 两次实际扣费，均 ¥0.20 |
| AutoDL Art 本 MCP 工作流，空闲 | 480p | ¥0.030/秒 | ¥0.15 | 页面报价，未实测 |
| AutoDL Art 本 MCP 工作流，高峰／空闲 | 768p | ¥0.050／0.040 每秒 | ¥0.25／0.20 | 页面报价，未实测 |
| MiniMax 官方 H3-Lite API | 480P | $0.025/秒 | 约 ¥0.84 | 官方目录价换算，未实测 |
| MiniMax 官方 H3-Max API | 480P | $0.050/秒 | 约 ¥1.68 | 官方目录价换算，未实测 |
| MiniMax 官方 H3-Lite API | 768P | $0.040/秒 | 约 ¥1.34 | 官方目录价换算，未实测 |
| MiniMax 官方 H3-Highspeed API | 768P | $0.060/秒 | 约 ¥2.01 | 官方目录价换算，未实测 |
| MiniMax 官方 H3 API | 768P | $0.080/秒 | 约 ¥2.69 | 官方目录价换算，未实测 |
| MiniMax 官方 H3-Max API | 768P | $0.080/秒 | 约 ¥2.69 | 官方目录价换算，未实测 |
| MiniMax 官方 H3 API | 2K | $0.130/秒 | 约 ¥4.37 | 官方目录价换算，未实测 |

官方美元费用按 2026-10-26 [国家外汇管理局中间价](https://www.safe.gov.cn/AppStructured/hlw/RMBQuery.do) 1 美元 ≈ ¥6.7162 换算；官方各行的 5 秒费用是每秒目录价乘 5 的算术值，具体可选时长须看 API 参数。官方 H3 的输入视频与超过免费张数的图片**另计费**，上表只算输出。来源：[MiniMax 官方定价](https://platform.minimax.io/docs/pricing/overview)、[AutoDL Art 工作流页面](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v_no_pic)。AutoDL Art 是封装后的托管 ComfyUI 工作流，与 MiniMax 官方 API 的模型档位、画质与处理过程未经同条件对照；仅比较公开价格，不能把价差当作同质服务折扣。[完整型号、类别、分辨率和输入素材价格](h3-price-matrix.md)。

## 常见问题

| 情况 | 处理 |
| --- | --- |
| 登录后找不到令牌创建入口 | 到[令牌管理](https://autodl.art/large-model/tokens)；若提示实名认证，在平台内完成并刷新。 |
| `AUTODL_ART_TOKEN is missing` 或请求被拒 | 核对钥匙串服务名、令牌分组 `ComfyUI`、启用状态与有效期；别把令牌贴进求助信息。 |
| `h3_art_quote` 与网页价格不同 | 估价是本地静态观察值；以网页实时报价为准，先停止生成。 |
| 估算价超过 ¥0.25 被拒 | 缩短时长或选择 480p；只有核对实际预算后，才调整本地阈值及平台令牌额度。 |
| 已提交却超时或没看到 `task_id` | **不要再次提交**；先到平台调用日志和账单找任务，避免重复扣费。 |
| 查询显示 `RUNNING` | 用同一 `task_id` 稍后查询；这不是再次付费提交。 |
| 一条完成后再次提交被拒 | 默认每个 MCP 进程只允许一条；确认账单后重启 MCP 进程。 |
| 下载失败 | 成功后尽快下载；签名链接可能过期。再次查询任务，必要时联系平台，不要为了下载失败再生成。 |

## 数据与许可

令牌只交给你信任的 MCP 进程使用。`outputs/` 不会被 Git 跟踪，但仍是你本机文件，分享前自行检查内容。公开仓库的 MIT 许可仅覆盖本仓库代码；若改为自行部署 H3 权重或提供面向第三方的服务，应阅读 [MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)。

需要自己控制 ComfyUI 的用户另看[私有 GPU 备用路线](private-comfyui.md)；它不是本说明书已真实出片的路线。
