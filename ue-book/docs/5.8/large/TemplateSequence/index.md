# Template Sequence

> Runtime for template sequences

| 属性 | 值 |
|---|---|
| 中文名 | 模板序列 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TemplateSequence` (Runtime), `TemplateSequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

Template Sequence 是 Unreal Sequencer 系统的扩展，提供**模板序列**功能。与普通 Level Sequence 不同，模板序列不绑定到特定对象，而是定义一套可复用的动画模板。运行时，模板序列会根据目标对象的绑定关系自动适配播放。

核心价值：**一次定义，多处复用**。避免为每个 Actor 重复创建相同的动画序列。

典型应用：摄像机动画模板应用于不同角色、相似动画行为共享、参数化的序列模板等。

## 使用场景

- 你需要为多个不同的 Actor 创建相同模式的摄像机动画 → 用 Template Sequence
- 你需要创建一个动画模板，在不同骨骼网格体上复用 → 用 Template Sequence
- 你在构建 Sequencer 工作流，需要参数化、可复用的序列资产 → 用 Template Sequence
- 你需要通过蓝图动态绑定对象到预定义的动画模板 → 用 Template Sequence

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`TemplateSequence`](TemplateSequence.md) | Runtime | 核心运行时模块，提供模板序列的资产类型、播放逻辑和对象绑定机制 |
| [`TemplateSequenceEditor`](TemplateSequenceEditor.md) | Editor | 编辑器模块，提供模板序列的创建、编辑和 Sequencer 集成工具 |

## 蓝图用法

TemplateSequence 模块暴露的核心蓝图能力主要围绕模板序列的绑定与播放。详细 API 请参阅各子模块文档。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BindableObject` | 将对象绑定到模板序列的插槽 | `UTemplateSequence` |
| `CreateBoundObjectInstantiation` | 运行时实例化绑定对象 | `UTemplateSequencePlayer` |

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequence.h"
```

详细 C++ API 及示例请参阅 [TemplateSequence](TemplateSequence.md) 和 [TemplateSequenceEditor](TemplateSequenceEditor.md) 模块文档。

## 模块依赖

依赖插件：**LevelSequenceEditor**（在 .uplugin 中声明）

| 模块 | 用途 |
|---|---|
| `LevelSequenceEditor` | Sequencer 编辑器集成（上游依赖） |
| `MovieScene` | MovieScene 框架核心（Sequencer 基础设施） |
| `MovieSceneTracks` | MovieScene 轨道实现 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 新日志宏 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复 Level Sequence Player 中编辑器专用属性导致的复制布局不匹配 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | Sequencer 对象绑定菜单新增"烘焙变换"功能 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除 UObject 中 7 个已废弃或仅工具使用的虚函数 |

### 维护评价

该插件处于**活跃维护**状态。2026 年有多次实质性更新，包括编译修复、日志系统迁移、复制同步 bug 修复以及 Sequencer 功能增强。

**注意事项**：
- `.uplugin` 标记为 `IsBetaVersion: true`，功能可能随版本变化
- `EnabledByDefault: false`，需在插件管理器中手动启用
- 虽然标记为 Beta，但已存在约 6 年，核心功能相对稳定

**推荐**：如需可复用的 Sequencer 动画模板，可放心使用。关注 Beta 状态带来的潜在 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
- [TemplateSequence 运行时模块](TemplateSequence.md)
- [TemplateSequenceEditor 编辑器模块](TemplateSequenceEditor.md)