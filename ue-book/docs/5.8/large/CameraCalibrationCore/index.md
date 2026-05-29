# Camera Calibration Core

> Supports lens distortion and camera calibration.

| 属性 | 值 |
|---|---|
| 中文名 | 相机校准核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `CameraCalibrationCore` (Runtime), `CameraCalibrationCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-05-27 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibrationCore) | |

## 用途

Camera Calibration Core 是虚幻引擎虚拟制作流程中的核心相机校准工具，用于解决**真实相机镜头畸变**与**虚拟场景合成**之间的匹配问题。

该插件提供了一套完整的镜头校准工作流：

- **镜头畸变建模**：通过 Nodal Offset 和畸变参数模型（如 Brown-Conrady）描述真实镜头的光学特性
- **校准数据采集**：支持从 Live Link 等外部源获取相机参数，自动计算畸变系数
- **畸变渲染应用**：将校准后的畸变参数应用到虚拟场景渲染中，确保合成画面与真实镜头视角一致
- **多镜头管理**：通过 Lens File 资产管理不同镜头的校准数据

简而言之：**让虚拟画面看起来像是用特定的真实镜头拍摄的**，是影视级虚拟制作（Virtual Production）不可或缺的基础设施。

## 使用场景

- **LED 虚拟摄影棚**：在 LED Volume 中拍摄时，需要确保虚拟背景与真实相机的镜头畸变完全匹配，避免合成画面出现"漂移"感
- **实时合成（Composure）**：通过 Composure 节点将畸变应用到最终合成输出
- **Live Link 相机跟踪**：接收来自跟踪系统的相机数据时，校准并补偿镜头畸变
- **MetaHuman 身份制作**：处理升级后的 MetaHuman 身份资产（涉及相机校准参数迁移）

## 模块列表

| 模块 | 类型 | 职责 |
|---|---|---|
| [`CameraCalibrationCore`](CameraCalibrationCore.md) | Runtime | 核心校准逻辑、畸变模型、Lens File 资产、Live Link 集成 |
| [`CameraCalibrationCoreEditor`](CameraCalibrationCoreEditor.md) | Editor | 编辑器 UI、镜头校准工具面板、资产编辑器定制 |

## 使用场景

- **LED 虚拟摄影棚拍摄**：使用 Unreal Stage 或 LiveLinkHub 进行实时虚拟制作时，校准镜头畸变以实现精准的 CG 与实景合成
- **相机跟踪数据校正**：当使用 Vicon/光学跟踪等外部系统时，需要补偿镜头畸变对跟踪精度的影响
- **实时合成（Composure）**：在 Composure 工作流中应用镜头畸变渲染，确保合成画面与真实镜头效果一致
- **影视后期预览**：在虚拟制片流程中提前预览镜头畸变效果，减少后期返工
- **多镜头管理**：在虚拟制片现场管理多个不同焦距/光圈镜头的校准数据

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibrationCore)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/VirtualProduction/CameraCalibration/)（虚幻引擎官方相机校准文档）