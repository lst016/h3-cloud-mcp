# 算力与方案调研

更新：2026-10-26，Asia/Taipei。价格是 AutoDL 算力市场观察值或官网公开标价，库存随时变化。以下不是实际出片成本实测。

| 路线 | 观察到的价格 | 判断 |
| --- | ---: | --- |
| AutoDL RTX 5090 32GB | ¥2.78–2.93/时 | 首选单卡，已有社区单卡 H3 部署案例；目标是先做真实 5 秒样片，再算每条成本。 |
| AutoDL RTX 4090 24GB | 约 ¥2.08/时 | 小时价较低，但 H3 量化路径可能发生显存卸载；只作为实测对照。 |
| AutoDL vGPU-32GB | 约 ¥1.66/时 | 纸面最便宜，实际算力、隔离和兼容性未验证，不宜直接判定每片最便宜。 |
| MiniMax 官方 API | 768p 标价 $0.08/生成秒；5 秒约 $0.40 | 省去模型下载和 GPU 空转，但不满足“租服务器跑开放权重”；适合作为质量与总成本对照。 |

“性价比”应以 `完整可用 MP4 的总价 = 实例开机时间 × 小时价 + 付费存储 + 重试消耗` 计算。至少对同一提示词记录冷启动与热运行各一条，检查音画、时长和失败率。第三方速度记录不当作本项目实测。

## 参考资料

- [MiniMax H3 官方模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3)：开放权重、FL2VA/Ref2VA、768p 与官方托管 2K 阶段的边界。
- [MiniMax H3 权重许可](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)：地域、商业与托管服务条款。
- [ComfyUI 原生 H3 节点](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py)：输入、帧数及节点接口。
- [AutoDL 计费规则](https://www.autodl.com/docs/price/)：开关机与付费数据盘计费。
- [AutoDL 实例数据保留](https://www.autodl.com/docs/instance_data/)：普通实例关机保留数据，连续关机 15 天会释放。
- [MiniMax 官方 API 定价](https://platform.minimax.io/subscribe/token-plan?tab=api-enterprise)：H3 768p 按生成秒计费。API 成片与本地低分辨率成片的质量、预处理阶段并不完全相同。
- [社区 AutoDL 5090 部署记录](https://github.com/JuneYaooo/minimax-h3-autodl)：59 GiB 双模型组合与部署检查项；代码未复制进本仓库。
- [社区 H3 MCP 案例](https://github.com/jonpojonpo/comfy-h3-mcp)：本地 ComfyUI MCP 工具范围参考；代码未复制进本仓库。
- [MCP Python SDK v2](https://github.com/modelcontextprotocol/python-sdk)：使用 `MCPServer` 的 stdio 实现。
