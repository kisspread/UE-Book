# Motion Design

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（核心运行时模块、编辑器工具、测试、UI资产） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 是一个功能全面的运动图形和动态设计工具集，专为虚拟制片、广播和实时图形制作而设计。它解决了在UE中高效创建、编辑、合成和播放复杂动态内容（如舞台视觉效果、电视节目包装、实时图形叠加）的需求。该插件提供了一个集成的、非破坏性的工作流，包含2D/3D元素设计、材质编辑、动画、序列化和媒体输出等完整管线。

## 使用场景

-   你正在为虚拟制片节目或现场活动制作舞台视觉、Logo动画和动态背景。
-   你需要设计和制作电视节目片头、片尾、字幕条（Lower Thirds）和数据可视化图形。
-   你在构建一个需要通过时间线精确控制图形元素动画和媒体播放的实时广播系统。
-   你需要一个包含修改器、克隆器、效果器、材质设计器的非破坏性创作流程。

## 蓝图用法

该插件包含大量模块，提供了丰富的蓝图API，但由于插件规模巨大，此处无法详尽列举。核心的蓝图接口通常封装在 `AvalancheCore`、`AvalancheMedia`、`AvalancheEffectors` 等模块中。建议通过虚幻编辑器的内容浏览器搜索相关资产（如 `AAvaShapeActor`， `UAvaSequence`）来探索可用的蓝图节点。

## C++ 用法

使用该插件通常涉及引用其核心模块来构建自定义的动态设计功能。以下为概念性示例。

### 头文件引入

```cpp
// 引用核心运行时模块
#include "AvalancheCore/Public/AvaOutlinerSubsystem.h"

// 引用编辑器模块（仅限编辑器代码）
#include "AvalancheEditor/Public/IAvaEditor.h"
```

### 基本用法

通过子系统与Motion Design系统交互。
（来源：基于 `AvaOutlinerSubsystem` 的接口推断）

```cpp
// 在运行时或编辑器代码中，获取Outliner子系统来访问场景结构
UAvaOutlinerSubsystem* OutlinerSubsystem = GEditor->GetEditorSubsystem<UAvaOutlinerSubsystem>();
if (OutlinerSubsystem)
{
    // 获取根项并遍历，这是Motion Design场景结构管理的核心
    const FAvaOutlinerItemPtr RootItem = OutlinerSubsystem->GetRootItem();
    // ... 进行遍历或查询操作
}
```

## Demo 示例

由于插件极其庞大（43个模块，2060+源文件），提供一个最小的、可编译的C++示例过于复杂，且无法脱离Motion Design的编辑器环境运行。最实用的“Demo”是：
1.  启用插件。
2.  通过 **窗口 (Window) -> 虚拟制片 (Virtual Production) -> 动态设计器 (Motion Design Designer)** 打开主工作区。
3.  使用界面上的工具（形状、文本、材质设计器、序列器）创建和动画化对象。
4.  通过 **场景设置 (Scene Settings)** 面板配置媒体输出和播放规则。

## 模块依赖

从 Build.cs 的依赖分析，该插件依赖大量 UE 子系统和特定插件。以下是**独特且关键**的依赖：

| 模块 | 用途 |
|---|---|
| `ActorModifierCore` | 核心修改器系统框架，是Motion Design非破坏性编辑的基础 |
| `Sequencer` | 用于动画序列化、时间线控制和播放 |
| `MediaCompositing`, `MediaIOFramework` | 媒体输入输出、合成和播放 |
| `GeometryScript`, `GeometryCache` | 用于程序化几何体生成和缓存 |
| `Text3D` | 创建和操作3D文本 |
| `SVGImporter` | 导入SVG文件用于2D图形元素 |
| `RemoteControl` | 支持通过网络进行参数控制 |
| `ClonerEffector`, `PropertyAnimator` (等) | 提供克隆、效果、属性动画等核心功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将“场景设置”和“大纲视图”等专用标签页分组到关卡编辑器中 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用“节目单页面”设置时，增加了对Movie Render Queue的分析支持 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中添加了页面加载选项（全部、下一个、已选） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用Text3D和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过通知客户端其关联或解除关联来规范必要的复制粘贴代码 |

### 维护评价

**活跃维护**。
-   该插件于2025年5月从实验性分支迁移至正式生产分支（VirtualProduction），标志着其稳定性和重要性获得认可。
-   根据近期提交记录，插件在2026年5月仍在频繁进行功能增强、工作流优化和集成改进（如MRQ分析、页面控制、编辑器UI重组）。
-   作为Epic Games官方维护的虚拟制作核心工具之一，预计将持续获得长期支持和更新。
-   **推荐使用**：对于从事虚拟制片、广播图形和实时动态内容制作的团队，这是UE中功能最完整、官方支持最全面的专业工具集。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/)（如果存在，通常在官方文档的“虚拟制片”部分）