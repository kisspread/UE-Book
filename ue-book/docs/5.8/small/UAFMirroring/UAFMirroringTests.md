# UAF Mirroring

> Keyframe mirroring for UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF关键帧镜像 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMirroring` (Runtime), `UAFMirroringUncookedOnly` (Runtime), `UAFMirroringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring) | |

## 用途

UAF Mirroring 是 Unreal Animation Framework (UAF) 的扩展插件，专门用于**动画关键帧的镜像操作**。该插件提供了将动画姿态（Pose）进行镜像翻转的能力，使得动画师能够快速创建角色的左/右对称动画。通过镜像工具，可以显著减少手动调整对称动画的工作量。

插件包含：
- **基础和附加镜像特性（Trait）**：用于在动画图中实现镜像逻辑。
- **辅助方法**：提供镜像UAF姿态的底层API。
- **图模板**：包含一个预定义的镜像节点模板，方便在动画图中使用。

## 使用场景

- **创建对称动画**：当角色有左/右对称的动作（如行走、奔跑、攻击）时，只需制作一侧动画，另一侧可通过镜像自动生成。
- **动画编辑器工具集成**：在动画编辑器中，利用镜像功能快速调整动画。
- **动画蓝图逻辑**：在动画蓝图中动态决定是否使用镜像动画。

## 蓝图用法

由于该插件处于实验阶段且未提供公开蓝图API，目前主要通过C++代码和动画图模板使用。预计未来版本将暴露蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "UAFMirroring.h"
```

### 基本用法

从首次提交信息推断，插件提供了镜像UAF姿态的辅助方法。以下为假设性示例（基于UAF常见用法）：

```cpp
// 假设存在一个UAF Pose对象
FUAFPose SourcePose;

// 使用镜像辅助函数创建镜像姿态
FUAFPose MirroredPose = UAFMirroringHelper::MirrorPose(SourcePose);

// 在动画图中应用镜像特性
// 通过动画图编辑器拖放镜像节点模板
```

### 进阶用法

结合镜像特性（Trait）和动画图，可以实现更复杂的镜像逻辑，例如条件镜像或部分骨骼镜像。具体用法需参考UAF文档和插件源码。

## Demo 示例

由于该插件主要提供底层API和动画图模板，没有独立的可运行Demo。使用示例需在动画编辑器中配合UAF插件完成。

## 模块依赖

插件依赖于UAF和UAFAnimGraph插件。在你的模块中，需要添加以下依赖（根据你使用的模块）：

| 模块 | 用途 |
|---|---|
| `UAF` | UAF核心框架 |
| `UAFAnimGraph` | UAF动画图编辑器支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志宏迁移至UE_LOGF，统一日志输出。 |
| 2026-03-10 | `24473b8e` | Fix direct reads of latent SharedData properties in UAF traits | 修复UAF特性中潜在共享数据属性直接读取的bug。 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 添加提交工具验证器，用于构建和运行UAF插件的低层测试。 |
| 2026-01-23 | `81bd488d` | UAF fix some incorrect comparison of invalid bone indicies, where 16bit was upcast to 32bit and comp | 修复UAF中无效骨骼索引的比较错误，其中16位值被向上转换为32位进行比较。 |
| 2026-01-23 | `9735f798` | UAF: Fix rename/move issues | 修复UAF的重命名和移动问题。 |

### 维护评价

该插件创建于2025年8月，处于**实验性**阶段，版本号为0.1。从提交历史看，**维护活跃**，最近6个月内有多次更新，主要集中在bug修复和稳定性提升。由于依赖于UAF插件（同样处于实验阶段），其稳定性取决于UAF的整体成熟度。

**推荐使用**：适合早期采用者和对动画镜像有迫切需求的开发者。请注意，作为实验性功能，未来API可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring/Tests)