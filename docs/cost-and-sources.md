# 算力与方案调研

更新：2026-10-26，Asia/Taipei。价格是 AutoDL 算力市场观察值或官网公开标价，库存随时变化。以下不是实际出片成本实测。

| 路线 | 观察到的价格 | 判断 |
| --- | ---: | --- |
| AutoDL Art 托管 H3 工作流 API | 480p ¥0.03–0.04/生成秒；768p ¥0.04–0.05/生成秒 | 无实例开机和权重下载；5 秒约 ¥0.15–0.25。MCP 已接入，一条 5 秒 480p 样片实际扣费 ¥0.20。 |
| AutoDL Art 社区 H3 应用镜像 | GPU 小时价需登录后按地区和库存核对；基础系统盘 ¥0.10/日 | 已预装 H3 和工作流，适合需要自己控制 ComfyUI 的用户；关机后系统盘继续计费。当前 MCP 可对接兼容的 ComfyUI，但该镜像尚未实测。 |
| AutoDL.com RTX 5090 32GB 手动部署 | ¥2.78–2.93/时 | 必须独立控制模型和环境时的单卡候选；需算入下载与冷启动。 |
| AutoDL RTX 4090 24GB | 约 ¥2.08/时 | 本仓库所用 NVFP4 编码器要求 Blackwell；4090 需更换编码器和工作流后单独验证。 |
| AutoDL vGPU-32GB（页面显示 RTX 4080S） | 约 ¥1.66/时 | 不是 Blackwell，本仓库 NVFP4 预设不支持；需要另一套量化方案。 |
| MiniMax 官方 H3 API | 768P 标价 $0.08/生成秒；5 秒 $0.40 | 官方完整 H3 的最低分辨率为 768P，适合作为同分辨率价格参考；与此 AutoDL Art 工作流不是同配置实测。 |
| MiniMax 官方 H3-Lite API | 480P 标价 $0.025/生成秒；5 秒 $0.125 | 官方价格最低的 H3 480P 档位，型号不同，不能直接推断与 AutoDL Art 的画质相同。 |

“性价比”应以 `完整可用 MP4 的总价 = 实例开机时间 × 小时价 + 付费存储 + 重试消耗` 计算。至少对同一提示词记录冷启动与热运行各一条，检查音画、时长和失败率。第三方速度记录不当作本项目实测。

本次手动部署试跑未生成视频。因未先检查 AutoDL Art 的现成 H3 社区应用而产生了可避免的开机时间；该试跑不能作为单条成片成本。

## AutoDL Art 实测与 MiniMax 官方 API 目录价

全部 H3 模型、任务类别、输入素材收费、AutoDL Art 18 个工作流及每个标价分辨率的高峰／空闲对比，见[完整价格矩阵](h3-price-matrix.md)。

按 2026-10-26 [国家外汇管理局人民币中间价](https://www.safe.gov.cn/AppStructured/hlw/RMBQuery.do)，100 美元 = ¥671.62，即 1 美元约 ¥6.7162。美元换算仅供比较，实际支付汇率及手续费可能不同。均按**请求生成 5 秒文生视频**计算；本次 AutoDL Art 下载的 MP4 长 5.167 秒，但账单按请求的 5 秒扣费。

| 路线 | 分辨率与模型 | 5 秒费用 | 与 AutoDL Art 实测 ¥0.20 比较 | 证据层级 |
| --- | --- | ---: | ---: | --- |
| AutoDL Art H3 工作流 `minimax_h3_lightx2v_no_pic` | 480p 横屏 | **¥0.20** | 基准 | 平台令牌账单实扣一次；[验收记录](validation.md) |
| MiniMax 官方 H3-Lite API | 480P | $0.125 ≈ **¥0.84** | 约 4.2 倍 | [官方目录价](https://platform.minimax.io/docs/pricing/overview)，未在本项目付费实测 |
| MiniMax 官方 H3-Lite API | 768P | $0.20 ≈ **¥1.34** | 约 6.7 倍 | 官方目录价，未在本项目付费实测；分辨率更高 |
| MiniMax 官方 H3 API | 768P | $0.40 ≈ **¥2.69** | 约 13.4 倍 | 官方目录价，未在本项目付费实测；分辨率更高 |
| AutoDL Art 同工作流 | 768p，高峰时段 | **¥0.25** | 约 1.25 倍 | [页面报价](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v_no_pic)，未提交任务 |

按**相同标称 768P**比较，AutoDL Art 高峰报价 ¥0.25，MiniMax 官方 H3-Lite 目录价折合约 ¥1.34、官方 H3 约 ¥2.69，分别约为 5.4 倍和 10.7 倍；这仍不是相同实现、参数与画质的对照实验。AutoDL Art 提供封装的 ComfyUI 工作流，官方 API 的 H3、H3-Lite 属不同服务档位。画质、声音、稳定性与排队时间应以同提示词的实际结果另行比较。

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
- [MiniMax 官方 API 定价](https://platform.minimax.io/docs/pricing/overview)：H3、H3-Highspeed、H3-Lite、H3-Max 的分辨率、输出与输入素材目录价。API 成片与 AutoDL Art 工作流的质量、预处理阶段并不完全相同。
- [社区 AutoDL 5090 部署记录](https://github.com/JuneYaooo/minimax-h3-autodl)：59 GiB 双模型组合与部署检查项；代码未复制进本仓库。
- [社区 H3 MCP 案例](https://github.com/jonpojonpo/comfy-h3-mcp)：本地 ComfyUI MCP 工具范围参考；代码未复制进本仓库。
- [MCP Python SDK v2](https://github.com/modelcontextprotocol/python-sdk)：使用 `MCPServer` 的 stdio 实现。
