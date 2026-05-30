# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、编辑器工具、测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime) 等共 43 个模块 |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（内部代号 Avalanche）是 UE5 面向**虚拟制片和广播电视**场景的专业合成、设计与播出工具集。它解决的核心问题是：在虚幻引擎内完成传统上需要外部软件（如 After Effects、Nuke）才能完成的 2D/3D 动态图形设计和实时播出流程。

该插件从 `Experimental` 目录正式迁移至 `VirtualProduction`，表明 Epic 认为其已达到生产就绪状态。整个插件包含 43 个模块、2060+ 个源文件，是 UE5 中规模最大的插件之一，涵盖：

- **属性动画系统**（PropertyAnimator）：对 Actor 属性进行关键帧/程序化动画
- **形状与文本**（Shapes/Text）：原生矢量形状和 3D 文字创建
- **克隆与效果器**（ClonerEffector）：粒子/阵列克隆 + 效果器控制
- **遮罩系统**（Mask）：基于几何体的材质遮罩
- **媒体合成**（Media）：视频输入/输出与合成管线
- **场景树与大纲视图**（SceneTree/Outliner）：自定义场景管理层
- **过渡与序列器集成**（Transition/Sequencer）：时间线动画与过渡效果
- **远程控制**（RemoteControl）：外部设备遥控
- **MRQ 集成**（MRQ）：Movie Render Queue 高质量渲染支持

## 使用场景

- 你在做广播电视虚拟场景设计 → 使用 Motion Design 的形状、文本和材质工具快速搭建动态图形
- 你需要实时控制 LED 墙上的动态内容 → 用媒体输出和远程控制模块
- 你要批量创建重复元素阵列并用效果器影响它们 → 使用 ClonerEffector
- 你需要对 Actor 的任意属性做程序化动画 → 使用 PropertyAnimator 系统
- 你要在虚幻内完成完整的 motion graphics 合成 → 使用完整的 Motion Design 工作流

---

## 子模块文档：AvalanchePropertyAnimatorEditor

本模块是 PropertyAnimator 系统的**编辑器侧扩展**，为 Motion Design 大纲视图（Outliner）提供属性动画器的显示、交互和拖放功能。

### 模块概览

| 属性 | 值 |
|---|---|
| 模块名 | `AvalanchePropertyAnimatorEditor` |
| 类型 | Runtime |
| 源文件数 | 5 |
| 职责 | 大纲视图中的属性动画器编辑器集成 |

### 核心类

#### FAvaPropertyAnimatorEditorModule

模块入口，负责注册大纲视图扩展。

```cpp
// Private/AvaPropertyAnimatorEditorModule.h
class FAvaPropertyAnimatorEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;   // 注册 Outliner 扩展
    virtual void ShutdownModule() override;  // 注销 Outliner 扩展

protected:
    void RegisterOutlinerItems();
    void UnregisterOutlinerItems();

    FDelegateHandle OutlinerProxiesExtensionDelegateHandle;
    FDelegateHandle OutlinerContextDelegateHandle;
    FDelegateHandle OutlinerDropHandlerDelegateHandle;
};
```

**职责**：在模块启动时向 Motion Design 大纲视图注册三类扩展——项目代理（Proxy）、上下文菜单（ContextMenu）和拖放处理器（DropHandler）。

#### FAvaPropertyAnimatorEditorOutliner

表示大纲视图中的一个**属性动画器条目**。

| 功能 | 说明 |
|---|---|
| 显示名称 | 返回动画器的自定义名称 |
| 图标 | 根据动画器类型返回对应图标 |
| 可见性控制 | 支持按可见性类型开关 |
| 选中行为 | 选中时聚焦到对应动画器所属 Actor |
| 删除支持 | 可从大纲中删除动画器 |
| 自动清理 | 监听动画器移除事件，自动从大纲中移除 |

#### FAvaPropertyAnimatorEditorOutlinerProxy

**代理类**：扫描 Actor 上的 `UPropertyAnimatorCoreComponent`，自动创建对应的动画器子条目。

- 绑定组件的更新委托，当动画器增删时动态刷新大纲
- 选择代理时选中父 Actor
- 支持删除操作（清除组件中所有动画器）

#### FAvaPropertyAnimatorEditorOutlinerDropHandler

**拖放处理器**：支持将动画器条目从一个 Actor 拖放到另一个 Actor，或拖放到另一个动画器上。

| 拖放目标 | 行为 |
|---|---|
| Actor | 将动画器移动到目标 Actor 的 PropertyAnimatorCoreComponent |
| Animator | 将动画器重新排序或合并 |

#### FAvaPropertyAnimatorEditorOutlinerContextMenu

上下文菜单扩展，为选中的动画器条目添加右键操作。

```cpp
// 扩展大纲右键菜单
static void OnExtendOutlinerContextMenu(UToolMenu* InToolMenu);
// 获取上下文中的动画器对象
static void GetContextObjects(const UAvaOutlinerItemsContext* InContext, TSet<UObject*>& OutObjects);
```

### 工作流程

```
1. 模块启动
   └─ RegisterOutlinerItems()
       ├─ 注册 Proxy 扩展 → 自动扫描 Actor 组件中的动画器
       ├─ 注册 ContextMenu 扩展 → 右键菜单支持
       └─ 注册 DropHandler 扩展 → 拖放支持

2. Actor 进入大纲
   └─ FAvaPropertyAnimatorEditorOutlinerProxy 创建
       └─ 扫描 UPropertyAnimatorCoreComponent
           └─ 为每个 UPropertyAnimatorCoreBase 创建 Outliner Item

3. 用户操作
   ├─ 选中动画器 → 聚焦到对应 Actor
   ├─ 右键 → 上下文菜单
   ├─ 拖放到其他 Actor → 移动动画器
   └─ 删除 → 从组件中移除动画器
```

### C++ 用法

本模块是纯编辑器集成模块，不暴露公共 API 给下游使用。它依赖 `AvalanchePropertyAnimator` 运行时模块提供的 `UPropertyAnimatorCoreBase` 和 `UPropertyAnimatorCoreComponent` 类。

若需在自己的编辑器工具中集成属性动画器，直接使用运行时模块的 API：

```cpp
#include "AvaPropertyAnimatorCoreComponent.h"
#include "AvaPropertyAnimatorCoreBase.h"

// 获取 Actor 上的动画器组件
UPropertyAnimatorCoreComponent* AnimatorComp = Actor->FindComponentByClass<UPropertyAnimatorCoreComponent>();
if (AnimatorComp)
{
    // 遍历所有动画器
    TArray<UPropertyAnimatorCoreBase*> Animators;
    AnimatorComp->GetAnimators(Animators);
}
```

### 模块依赖

| 模块 | 用途 |
|---|---|
| `AvalancheOutliner` | Motion Design 自定义大纲视图框架 |
| `AvalanchePropertyAnimator` | 属性动画器运行时核心 |
| `PropertyAnimatorCore` | 底层属性动画器基础类 |
| `Sequencer` | 序列器集成 |

---

## 整体模块列表

<details>
<summary>点击展开全部 43 个模块</summary>

| 模块名 | 类型 | 职责 |
|---|---|---|
| `Avalanche` | Runtime | 插件主模块 |
| `AvalancheAttribute` | Runtime | 属性系统 |
| `AvalancheAttributeEditor` | Runtime | 属性编辑器 |
| `AvalancheCamera` | Runtime | 相机系统 |
| `AvalancheComponentVisualizers` | Runtime | 组件可视化器 |
| `AvalancheCore` | Runtime | 核心框架 |
| `AvalancheEditor` | Runtime | 编辑器核心 |
| `AvalancheEditorCore` | Runtime | 编辑器核心工具 |
| `AvalancheEffectors` | Runtime | 效果器系统 |
| `AvalancheEffectorsEditor` | Runtime | 效果器编辑器 |
| `AvalancheFunctionalTest` | Runtime | 功能测试 |
| `AvalancheInteractiveTools` | Runtime | 交互工具（编辑器） |
| `AvalancheInteractiveToolsRuntime` | Runtime | 交互工具（运行时） |
| `AvalancheLevelViewport` | Runtime | 关卡视口集成 |
| `AvalancheMRQ` | Runtime | Movie Render Queue 集成 |
| `AvalancheMRQEditor` | Runtime | MRQ 编辑器 |
| `AvalancheMask` | Runtime | 遮罩系统 |
| `AvalancheMaskEditor` | Runtime | 遮罩编辑器 |
| `AvalancheMaterial` | Runtime | 材质系统 |
| `AvalancheMedia` | Runtime | 媒体系统 |
| `AvalancheMediaEditor` | Runtime | 媒体编辑器 |
| `AvalancheModifiers` | Runtime | 修改器系统 |
| `AvalancheModifiersEditor` | Runtime | 修改器编辑器 |
| `AvalancheOutliner` | Runtime | 大纲视图 |
| `AvalanchePropertyAnimator` | Runtime | 属性动画器 |
| `AvalanchePropertyAnimatorEditor` | Runtime | 属性动画器编辑器 |
| `AvalancheRemoteControl` | Runtime | 远程控制 |
| `AvalancheRemoteControlEditor` | Runtime | 远程控制编辑器 |
| `AvalancheSVGEditor` | Runtime | SVG 编辑器 |
| `AvalancheSceneRig` | Runtime | 场景装配 |
| `AvalancheSceneRigEditor` | Runtime | 场景装配编辑器 |
| `AvalancheSceneTree` | Runtime | 场景树 |
| `AvalancheSequence` | Runtime | 序列系统 |
| `AvalancheSequencer` | Runtime | 序列器集成 |
| `AvalancheShapes` | Runtime | 形状系统 |
| `AvalancheShapesEditor` | Runtime | 形状编辑器 |
| `AvalancheTag` | Runtime | 标签系统 |
| `AvalancheTagEditor` | Runtime | 标签编辑器 |
| `AvalancheText` | Runtime | 文本系统 |
| `AvalancheTextEditor` | Runtime | 文本编辑器 |
| `AvalancheTransition` | Runtime | 过渡系统 |
| `AvalancheTransitionEditor` | Runtime | 过渡编辑器 |
| `AvalancheViewport` | Runtime | 视口系统 |

</details>

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 面板从关卡编辑器分离为独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为 MRQ 的 Rundown 页面设置添加分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在演出控制工具栏添加页面加载选项（全部/下一个/已选） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：重构客户端关联/解除关联通知逻辑 |

### 维护评价

**维护状态：🟢 活跃维护**

- 插件创建于 2025 年 5 月，至今约 1 年
- **持续高频更新**：最近的提交集中在 2026 年 5 月，几乎每天都有改动
- 由 Epic Games 核心虚拟制片团队维护（juan portillo 等）
- 从 Experimental 正式迁移至 VirtualProduction，表明已达到生产级别
- 43 个模块的规模意味着这是一个**战略级插件**，Epic 有长期投入计划
- **推荐使用**：如果你的项目涉及虚拟制片、广播或动态图形设计，这是官方推荐的首选工具链

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [AvalanchePropertyAnimatorEditor 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalanchePropertyAnimatorEditor)