# H3 视频价格全表：MiniMax 官方 API 与 AutoDL Art

核对日期：2026-10-26。以下覆盖当日 MiniMax 官方 H3 系列的全部**模型、输出分辨率和任务类别**，以及 AutoDL Art H3 目录中的 **18 个工作流及其全部标价分辨率**。官方价格为美元目录价，AutoDL Art 价格为页面人民币报价；只有文生视频 `minimax_h3_lightx2v_no_pic` 的 480p、请求 5 秒有一次实际扣费记录。没有为制作本表再提交付费任务。

换算采用 [国家外汇管理局 2026-10-26 人民币汇率中间价](https://www.safe.gov.cn/AppStructured/hlw/RMBQuery.do)：100 美元 = ¥671.62。人民币数值仅为按 1 美元 = ¥6.7162 的算术换算，不代表 MiniMax 收款汇率、手续费或含税成交价。报价会变动，提交任务前应重新打开来源页面核对。

## MiniMax 官方 H3：全部模型与输出分辨率

[官方视频定价表](https://platform.minimax.io/docs/pricing/overview)将输出、输入视频和超过免费额度的输入图片分开计费。下表中的「5 秒输出」是按每秒单价乘 5 的**算术估算，只包含输出视频**，不包含可能产生的输入素材费用；具体可请求的时长以相应 API 参数为准。

| 模型 | 输出分辨率 | 输出 $/秒 | 输出约 ¥/秒 | 5 秒输出 $ / 约 ¥ | 输入视频 $/秒 | 超额输入图 $/张 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| H3-Lite | 480P | 0.025 | 0.168 | 0.125 / 0.84 | 0.025 | 0.02 |
| H3-Lite | 768P | 0.040 | 0.269 | 0.200 / 1.34 | 0.040 | 0.02 |
| H3-Highspeed | 768P | 0.060 | 0.403 | 0.300 / 2.01 | 0.060 | 0.03 |
| H3 | 768P | 0.080 | 0.537 | 0.400 / 2.69 | 0.080 | 0.04 |
| H3 | 2K | 0.130 | 0.873 | 0.650 / 4.37 | 0.130 | 0.04 |
| H3-Max | 480P | 0.050 | 0.336 | 0.250 / 1.68 | 0.0553 | 0.074 |
| H3-Max | 768P | 0.080 | 0.537 | 0.400 / 2.69 | 0.1430 | 0.074 |

**任务类别：**上述四个模型均支持文生视频、图生视频、首尾帧视频，以及图片／视频／音频参考。官方说明：在同一模型和输出分辨率下，这些任务的**输出视频单价相同**；输入音频免费。H3、Highspeed、Lite 每任务前 5 张输入图免费，之后按表中每张计费；H3-Max 前 2 张免费。输入视频另按**输入秒数**和表中价格计费。因此「有参考素材」不一定与纯文生视频同总价。例如 H3 768P 输出 5 秒并输入 5 秒参考视频，目录价为 `5×$0.08 + 5×$0.08 = $0.80`，约 ¥5.37；若没有输入视频且图片在免费额度内，输出部分为 $0.40，约 ¥2.69。[官方说明](https://platform.minimax.io/docs/pricing/overview)

**官方另列两类能力：**H3-Regeneration 将 H3 已产出的 768P 视频重生成 2K，新增输出费 $0.05/秒；原任务的输入材料再次计费（前 5 张图免费，超额 $0.025/张，输入视频 $0.05/秒，音频免费），**原生成任务费用仍需另算**。H3-Context-IR 按 token 计费：输入 $0.90／百万 token、输出 $3.60／百万 token，无法直接换算为每条视频费用。[官方说明](https://platform.minimax.io/docs/pricing/overview)

## AutoDL Art：全部 H3 工作流及标价分辨率

下表来自 [AutoDL Art H3 工作流目录](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v_no_pic)中逐个打开的 18 个工作流详情页。单元格均为**高峰 / 空闲，人民币每生成秒**；高峰栏标为 08:00–24:00，空闲栏标为 00:00–08:00，页面未在价格表中注明时区。`—` 表示该工作流页面没有列出此档，不能当成可用分辨率。名称中的「高速」「画质增强」是工作流标签，不等于官方 API 的 H3-Highspeed 型号或官方 2K 档。

| 类别 | AutoDL Art 工作流 ID（点击查价） | 480p | 736p | 768p | 1080p | 1088p | 1440p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 文生 | [`minimax_h3_lightx2v_no_pic`](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v_no_pic) | 0.040 / 0.030 | — | 0.050 / 0.040 | — | — | — |
| 文生 | [`minimax_h3_b99_001`](https://www.autodl.art/large-model/comfyui/minimax_h3_b99_001) | — | 0.060 / 0.040 | — | — | — | — |
| 文生（高质量） | [`minimax_h3_z0901`](https://www.autodl.art/large-model/comfyui/minimax_h3_z0901) | 0.050 / 0.040 | — | 0.080 / 0.060 | — | 0.080 / 0.060 | 0.090 / 0.070 |
| 首尾帧 | [`minimax_h3_lightx2v`](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v) | 0.040 / 0.030 | — | 0.050 / 0.040 | — | — | — |
| 首尾帧 | [`minimax_h3_b99_002`](https://www.autodl.art/large-model/comfyui/minimax_h3_b99_002) | — | 0.060 / 0.040 | — | — | — | — |
| 多图参考 | [`minimax_h3_lightx2v_v5`](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v_v5) | 0.040 / 0.030 | — | 0.050 / 0.040 | 0.100 / 0.060 | — | — |
| 多图参考，最长 15 秒 | [`minimax_h3_lightx2v_v5_15s`](https://www.autodl.art/large-model/comfyui/minimax_h3_lightx2v_v5_15s) | 0.040 / 0.030 | — | 0.050 / 0.040 | — | — | — |
| 多图参考，最长 12 秒 | [`minimax_h3_b99_003_12s`](https://www.autodl.art/large-model/comfyui/minimax_h3_b99_003_12s) | — | 0.060 / 0.040 | — | — | — | — |
| 六图参考 | [`minimax_h3_z0902`](https://www.autodl.art/large-model/comfyui/minimax_h3_z0902) | 0.050 / 0.040 | — | 0.080 / 0.060 | — | 0.080 / 0.060 | 0.090 / 0.070 |
| 多图＋音频同步 | [`minimax_h3_image_audio_to_video`](https://www.autodl.art/large-model/comfyui/minimax_h3_image_audio_to_video) | 0.040 / 0.030 | — | 0.050 / 0.040 | 0.100 / 0.060 | — | — |
| 多图＋多音频 | [`minimax_h3_image_audio_to_video_v2`](https://www.autodl.art/large-model/comfyui/minimax_h3_image_audio_to_video_v2) | 0.040 / 0.030 | — | 0.050 / 0.040 | 0.110 / 0.070 | — | — |
| 多图＋多音频，最长 15 秒 | [`minimax_h3_image_audio_to_video_v2_15s`](https://www.autodl.art/large-model/comfyui/minimax_h3_image_audio_to_video_v2_15s) | 0.040 / 0.030 | — | 0.050 / 0.040 | — | — | — |
| 多图＋多音频（升级画质） | [`minimax_h3_zm_u24`](https://www.autodl.art/large-model/comfyui/minimax_h3_zm_u24) | 0.040 / 0.030 | — | 0.050 / 0.040 | — | — | — |
| 多图＋多音频（高速） | [`minimax_h3_zm_u08`](https://www.autodl.art/large-model/comfyui/minimax_h3_zm_u08) | 0.040 / 0.030 | — | 0.050 / 0.040 | — | — | — |
| 六图＋三音频 | [`minimax_h3_z0903`](https://www.autodl.art/large-model/comfyui/minimax_h3_z0903) | 0.050 / 0.040 | — | 0.080 / 0.060 | — | 0.080 / 0.060 | 0.090 / 0.070 |
| 九图＋三音频，15 秒画质增强 | [`minimax_h3_803`](https://www.autodl.art/large-model/comfyui/minimax_h3_803) | 0.040 / 0.030 | — | 0.050 / 0.040 | — | 0.060 / 0.050 | 0.070 / 0.060 |
| 九图，15 秒画质增强 | [`minimax_h3_802`](https://www.autodl.art/large-model/comfyui/minimax_h3_802) | 0.040 / 0.030 | — | 0.050 / 0.040 | — | 0.060 / 0.050 | 0.070 / 0.060 |
| 九图，15 秒无字幕 | [`minimax_h3_801`](https://www.autodl.art/large-model/comfyui/minimax_h3_801) | 0.050 / 0.040 | — | 0.060 / 0.050 | — | 0.070 / 0.060 | 0.080 / 0.070 |

Art 表中 **480p、736p、768p、1080p、1088p、1440p** 是六个独立标价档；未列 2K。页面没有统一披露额外素材费用、每个工作流的实际输出尺寸与计费秒数取整方式，因此只能把表中价格视为提交前报价，不能推断所有工作流的成片质量或最终账单一致。单条理论报价为 `所选单价 × 请求生成秒数`，如 5 秒 × ¥0.04/秒 = ¥0.20。15 秒、12 秒工作流的名称表示最长时长，不表示所有请求固定按 15 秒或 12 秒收费；实际允许时长以该工作流 API 参数为准。

## 同分辨率价格与实际扣费

| 对照场景 | AutoDL Art 报价或实扣 | MiniMax 官方目录价（约人民币） | 价格关系与限制 |
| --- | ---: | ---: | --- |
| 480p 文生，5 秒 | Art 已实扣 **¥0.20**（高峰 ¥0.040/秒；空闲报价 ¥0.15） | H3-Lite **¥0.84**；H3-Max **¥1.68** | 官方输出费约为实扣的 4.2 倍、8.4 倍；型号和工作流不同 |
| 768p 文生，5 秒 | Art 基础文生高峰 **¥0.25**；空闲 **¥0.20**（均为报价） | H3-Lite **¥1.34**；Highspeed **¥2.01**；H3 **¥2.69**；H3-Max **¥2.69** | 与 Art 高峰价相比，官方输出费约为 5.4、8.1、10.7、10.7 倍；均未同条件实测 |
| 高于 768p | Art 1080p / 1088p / 1440p 各有不同工作流报价，详见上表 | 官方 H3 的 2K 输出约 **¥4.37／5 秒** | 名称及实际像素、模型与处理过程未统一，不做同分辨率倍数比较 |

本仓库一条文生视频请求 5 秒，AutoDL Art 返回的 MP4 实长 5.167 秒、864×480，API 令牌账单实扣 ¥0.20；参见[验收记录](validation.md)。其余 AutoDL Art 行均为页面标价，官方 API 行均为目录价换算，**没有做同提示词、同参数、同服务条件的画质／速度／成功率对照实验**。[官方视频资源包说明](https://platform.minimax.io/docs/pricing/overview)写明 H3 尚不适用该资源包；[MiniMax M Plan](https://platform.minimax.io/subscribe/coding-plan)中部分档位另含 H3 配额，属于不同计费方式，不能把视频资源包折扣或 M Plan 的订阅价直接套进本表的按量单价。

## 范围外：官方旧版 Hailuo 视频模型

为避免将「所有类别」误解成只列 H3，下表补充同一官方定价页列出的旧版视频模型。它们是**按整条视频**定价，不属于 H3，也没有与上面的 AutoDL Art H3 工作流做同模型对比。

| 官方旧版模型 | 输出规格 | 美元／条 | 约人民币／条 |
| --- | --- | ---: | ---: |
| Hailuo-2.3-Fast | 768P，6 秒 | 0.19 | 1.28 |
| Hailuo-2.3-Fast | 768P，10 秒 | 0.32 | 2.15 |
| Hailuo-2.3-Fast | 1080P，6 秒 | 0.33 | 2.22 |
| Hailuo-2.3 | 768P，6 秒 | 0.28 | 1.88 |
| Hailuo-2.3 | 768P，10 秒 | 0.56 | 3.76 |
| Hailuo-2.3 | 1080P，6 秒 | 0.49 | 3.29 |
| Hailuo-02 | 512P，6 秒 | 0.10 | 0.67 |
| Hailuo-02 | 512P，10 秒 | 0.15 | 1.01 |
| Hailuo-02 | 768P，6 秒 | 0.28 | 1.88 |
| Hailuo-02 | 768P，10 秒 | 0.56 | 3.76 |
| Hailuo-02 | 1080P，6 秒 | 0.49 | 3.29 |

来源：[MiniMax 官方视频定价页](https://platform.minimax.io/docs/pricing/overview)。
