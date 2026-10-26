# 算力与方案调研

更新：2026-10-26，Asia/Taipei。价格是 AutoDL 算力市场观察值或官网公开标价，库存随时变化。以下不是实际出片成本实测。

| 路线 | 观察到的价格 | 判断 |
| --- | ---: | --- |
| AutoDL Art 托管 H3 工作流 API | 480p ¥0.03–0.04/生成秒；768p ¥0.04–0.05/生成秒 | 无实例开机和权重下载；5 秒约 ¥0.15–0.25。少量出片优先核对这条路线。MCP 已接入，实际出片尚待验收。 |
| AutoDL Art 社区 H3 应用镜像 | GPU 小时价需登录后按地区和库存核对；基础系统盘 ¥0.10/日 | 已预装 H3 和工作流，适合需要自己控制 ComfyUI 的用户；关机后系统盘继续计费。当前 MCP 可对接兼容的 ComfyUI，但该镜像尚未实测。 |
| AutoDL.com RTX 5090 32GB 手动部署 | ¥2.78–2.93/时 | 必须独立控制模型和环境时的单卡候选；需算入下载与冷启动。 |
| AutoDL RTX 4090 24GB | 约 ¥2.08/时 | 本仓库所用 NVFP4 编码器要求 Blackwell；4090 需更换编码器和工作流后单独验证。 |
| AutoDL vGPU-32GB（页面显示 RTX 4080S） | 约 ¥1.66/时 | 不是 Blackwell，本仓库 NVFP4 预设不支持；需要另一套量化方案。 |
| MiniMax 官方 API | 768p 标价 $0.08/生成秒；5 秒约 $0.40 | 省去模型下载和 GPU 空转，但不满足“租服务器跑开放权重”；适合作为质量与总成本对照。 |

“性价比”应以 `完整可用 MP4 的总价 = 实例开机时间 × 小时价 + 付费存储 + 重试消耗` 计算。至少对同一提示词记录冷启动与热运行各一条，检查音画、时长和失败率。第三方速度记录不当作本项目实测。

本次手动部署记录：AutoDL.com 的 96GB PRO6000 实例于 2026-10-26 关机，账单支出 ¥7.60，未生成视频。两个 VAE 已通过 SHA-256，主模型下载接近完成，文字编码器未完成。因未先检查 AutoDL Art 的现成 H3 社区应用而产生了可避免的开机时间；此试跑不能作为单条成片成本。

## 参考资料

- [MiniMax H3 官方模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3)：开放权重、FL2VA/Ref2VA、768p 与官方托管 2K 阶段的边界。
- [MiniMax H3 权重许可](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)：地域、商业与托管服务条款。
- [ComfyUI 原生 H3 节点](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py)：输入、帧数及节点接口。
- [AutoDL 计费规则](https://www.autodl.com/docs/price/)：开关机与付费数据盘计费。
- [AutoDL 实例数据保留](https://www.autodl.com/docs/instance_data/)：普通实例关机保留数据，连续关机 15 天会释放。
- [AutoDL Art H3 社区应用](https://www.autodl.art/app/market/252)：预装 H3，列出文生、图生等工作流，并标称支持 API。
- [AutoDL Art 托管 H3 文生视频](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v_no_pic)：当前 480p/768p 按生成秒报价，具体以提交前页面为准。
- [AutoDL Art 应用计费](https://autodl.art/docs/app/)：实例按开关机秒数收费，系统盘即使关机仍按日计费。
- [AutoDL Art ComfyUI API](https://autodl.art/docs/comfyui_api/)：提交与查询两个端点，返回的成片 URL 有效期较短。
- [MiniMax 官方 API 定价](https://platform.minimax.io/subscribe/token-plan?tab=api-enterprise)：H3 768p 按生成秒计费。API 成片与本地低分辨率成片的质量、预处理阶段并不完全相同。
- [社区 AutoDL 5090 部署记录](https://github.com/JuneYaooo/minimax-h3-autodl)：59 GiB 双模型组合与部署检查项；代码未复制进本仓库。
- [社区 H3 MCP 案例](https://github.com/jonpojonpo/comfy-h3-mcp)：本地 ComfyUI MCP 工具范围参考；代码未复制进本仓库。
- [MCP Python SDK v2](https://github.com/modelcontextprotocol/python-sdk)：使用 `MCPServer` 的 stdio 实现。
