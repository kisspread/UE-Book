# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 低频音频编辑系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个高级别的音频创作与播放系统。它并非一个简单的音频播放器，而是提供了一套完整的音频事件编辑器、参数绑定系统和执行器，允许音频设计师以数据驱动的方式定义复杂的音频行为。该插件旨在为游戏音频系统提供一种结构化、可编辑、可调试的创作流程，取代传统的纯代码或纯资产驱动的音频实现方式。

## 使用场景

- 你需要为游戏事件（如开火、拾取、脚步声）创建复杂的、带有条件逻辑和参数的音频反馈。
- 你需要一个集成在编辑器中的音频事件编辑器，能够可视化地编辑音频事件树和参数绑定。
- 你希望音频逻辑与游戏代码解耦，允许音频设计师独立调整音频行为而无需修改 C++ 代码。

## 蓝图用法

基于提供的源码分析，Subsonic 主要提供了一个编辑器资产（`USubsonicEventCollection`）及其配套的编辑器工具。虽然当前代码片段没有直接暴露 `BlueprintCallable` 函数，但系统的核心是通过创建和编辑 `SubsonicEventCollection` 资产来定义音频事件。

### 核心资产

- **SubsonicEventCollection**: 这是 Subsonic 系统的核心资产。音频设计师可以在自定义的编辑器（`FEventCollectionEditor`）中编辑它。
    - **事件树 (Event Tree)**：定义一系列音频事件，每个事件可以包含多个动作（Actions）。
    - **参数绑定 (Property Binding)**：允许将游戏运行时的参数（如速度、方向）绑定到音频动作的属性上，实现动态音频变化。

### 编辑器界面

通过 `USubsonicEventCollectionFactory` 创建新资产，双击打开后进入 `FEventCollectionEditor`，其中包含：
1. **事件树 (Event Tree)**：显示事件和动作的层级结构。
2. **细节面板 (Details View)**：编辑选中的事件或动作的属性。
3. **参数面板 (Parameters View)**：管理集合级别和事件级别的参数包（Property Bag）。
4. **传输控件 (Transport Controls)**：包含试听（Audition）和停止按钮，用于在编辑器中预览音频效果。

## C++ 用法

由于这是一个实验性且以编辑器为中心的系统，C++ 用法主要涉及扩展其编辑器功能或与其核心数据结构交互。

### 头文件引入

```cpp
#include "SubsonicCore.h" // 用于核心数据结构
#include "SubsonicEditor.h" // 用于编辑器扩展
```

### 基本用法：与事件集合交互

以下示例展示了如何获取和修改一个 `USubsonicEventCollection` 的底层数据结构。

```cpp
// 假设你已经获得了一个 USubsonicEventCollection 指针 (Collection)
#include "SubsonicCore.h"

// 获取其核心定义结构（注意：直接访问结构通常在事务上下文中进行）
const UE::Subsonic::Core::FSubsonicEventCollectionDefinition& CollectionDef = Collection->GetCollectionDefinition();

// 例如，遍历所有事件
for (const UE::Subsonic::Core::FSubsonicEvent& Event : CollectionDef.Events)
{
    UE_LOG(LogTemp, Log, TEXT("Event Name: %s"), *Event.Name.ToString());
    // 遍历该事件下的所有动作
    for (const UE::Subsonic::Core::FSubsonicEventActionDefinition& Action : Event.Actions)
    {
        UE_LOG(LogTemp, Log, TEXT("  Action Struct: %s"), *Action.ActionStruct ? *Action.ActionStruct->GetName() : TEXT("Null"));
    }
}
```

### 进阶用法：扩展编辑器

`FEventCollectionEditor` 类提供了扩展点。你可以通过继承或组合来扩展其功能。例如，`FSubsonicPropertyBindingExtension` 展示了如何为属性面板添加自定义绑定下拉菜单。

```cpp
// 示例：自定义属性绑定扩展（概念代码）
class FMyCustomBindingExtension : public UE::Subsonic::Editor::FSubsonicPropertyBindingExtension
{
public:
    // 覆盖 IsPropertyExtendable 以控制哪些属性显示自定义绑定
    virtual bool IsPropertyExtendable(const UClass* InObjectClass, const IPropertyHandle& InPropertyHandle) const override
    {
        // 只对特定类型的属性生效
        return InObjectClass->IsChildOf<UMyAudioAction>() && 
               InPropertyHandle->GetProperty()->GetFName() == GET_MEMBER_NAME_CHECKED(UMyAudioAction, Volume);
    }
};
```

## Demo 示例

创建一个简单的音频事件集合，包含一个事件和一个音量参数。

**创建步骤：**
1.  在内容浏览器中右键 -> Audio -> Subsonic Event Collection。
2.  双击打开资产，进入 Subsonic Event Collection Editor。
3.  在事件树中，右键 -> 添加事件。命名为“PlayGunshot”。
4.  选中“PlayGunshot”事件，在细节面板中，找到“参数”部分，添加一个新的浮点参数，命名为“VolumeMultiplier”。
5.  在“PlayGunshot”事件下，右键 -> 添加动作。从类型列表中选择一个声音波形（SoundWave）动作。
6.  选中这个新动作，在细节面板中，找到“Volume Multiplier”属性。点击属性右侧的绑定图标，选择“VolumeMultiplier”参数进行绑定。

现在，当在游戏代码中触发“PlayGunshot”事件时，可以通过设置“VolumeMultiplier”参数来动态控制音量。

## 模块依赖

Subsonic 插件本身提供了完整的模块栈。如果你希望在自己的项目模块中集成或扩展 Subsonic，你需要依赖以下插件模块：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | 提供核心数据结构（如事件、动作定义），是运行时数据的基础。 |
| `SubsonicEditor` | 提供编辑器UI、资产编辑器、自定义细节面板等。仅用于编辑器模块。 |
| `SubsonicEngine` | 提供音频引擎的执行器（Executor）和播放逻辑，负责在运行时根据定义驱动音频。 |
| `SubsonicEngineTest` | 包含针对 SubsonicEngine 的测试用例。仅用于开发和测试。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复一次错误的合并，回滚了对 Subsonic 订阅者系统的全面修改，并应用了最小的、非废弃性的修改。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃修复相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静默了 PVS 静态分析工具的警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“添加”菜单中增加了新的“音频”子菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |

### 维护评价

- **状态**：实验性且活跃开发中。
- **分析**：该插件创建于 2026 年初，至今（2026年5月）仍在频繁更新。近期的提交主要集中在修复合并问题、解决编译警告和改进编辑器工作流（如内容浏览器集成）。这表明它正在积极开发和完善中。
- **风险**：由于标记为 `IsExperimentalVersion: true`，其 API 和内部结构没有稳定性保证，未来版本可能发生重大变更。`SubsonicEngineTest` 模块的存在表明开发团队重视测试，这对稳定性是积极信号。
- **推荐**：适合希望尝试下一代音频创作工作流的项目和开发者，但应做好应对频繁变更和潜在重构的准备。不推荐用于需要长期稳定维护的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档]()（暂无）
- [测试用例]()（位于 `SubsonicEngineTest` 模块中，但未提供具体路径）