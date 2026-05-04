# RigLogic Plugin v10.3.0

> RigLogic Plugin for Facial Animation v10.3.0

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（DNA资产、蓝图资产） |
| 模块 | `RigLogicLib` (Runtime), `RigLogicModule` (Runtime), `RigLogicEditor` (Runtime), `RigLogicDeveloper` (Runtime), `RigLogicLibTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic) | |

## 用途

RigLogic 是一个用于驱动高保真、基于数据的面部动画的运行时系统。它主要服务于 MetaHuman 等需要极高面部细节和真实感的角色。该插件的核心是解析和运行由 DNA（数字基因）文件定义的复杂面部骨骼、变形目标和逻辑，从而实现基于骨骼、混合形状或两者混合的实时面部动画驱动。它解决了传统面部动画系统在复杂度、性能和跨平台一致性上的挑战。

## 使用场景

-   你正在使用 **MetaHuman** 角色，并希望获得其完整的、基于 DNA 的面部动画能力。
-   你需要一个高性能的运行时系统来驱动包含数百个骨骼和混合形状的复杂面部动画。
-   你的项目需要跨平台（PC、主机、移动端）保持一致的面部动画表现。
-   你需要将外部工具（如 Maya）中创建的面部绑定逻辑（DNA）无缝集成到 Unreal Engine 中。

## 蓝图用法

RigLogic 提供了蓝图友好的接口，主要用于组件的初始化和控制。核心功能通过 `URigLogicComponent` 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load DNA` | 从资产或字节数组加载 DNA 数据。 | `URigLogicComponent` |
| `Set Skeletal Mesh` | 为组件设置要驱动的骨骼网格体。 | `URigLogicComponent` |
| `Set LOD Index` | 设置当前使用的细节层次（LOD）索引。 | `URigLogicComponent` |
| `Get Control Values` | 获取当前所有控制值的数组。 | `URigLogicComponent` |
| `Set Control Values` | 设置控制值以驱动面部动画。 | `URigLogicComponent` |

### 使用示例（蓝图描述）

1.  在你的角色蓝图中，添加一个 `RigLogicComponent`。
2.  在 `BeginPlay` 事件中，调用 `Load DNA` 节点，传入你的 DNA 资产。
3.  调用 `Set Skeletal Mesh` 节点，将角色的骨骼网格体引用传入。
4.  在动画蓝图或角色蓝图中，通过 `Set Control Values` 节点，根据游戏逻辑（如对话系统、表情输入）设置控制值，驱动面部动画。
5.  可以使用 `Get Control Values` 来读取当前状态，用于UI显示或逻辑判断。

## C++ 用法

C++ 用法提供了更底层和高效的控制。核心类是 `URigLogicComponent`。

### 头文件引入

```cpp
#include “RigLogicComponent.h”
```

### 基本用法

```cpp
// 在角色类中获取或创建组件
URigLogicComponent* RigLogicComp = FindComponentByClass<URigLogicComponent>();
if (!RigLogicComp)
{
    RigLogicComp = NewObject<URigLogicComponent>(this);
    RigLogicComp->RegisterComponent();
}

// 加载 DNA
URigLogicDNAAsset* DNAAsset = LoadObject<URigLogicDNAAsset>(nullptr, TEXT(“/Game/Characters/MyMetaHuman/Face_MyMetaHuman.dna”));
RigLogicComp->LoadDNA(DNAAsset);

// 设置骨骼网格体
USkeletalMesh* FaceMesh = LoadObject<USkeletalMesh>(nullptr, TEXT(“/Game/Characters/MyMetaHuman/Face_MyMetaHuman”));
RigLogicComp->SetSkeletalMesh(FaceMesh);

// 在 Tick 或动画更新中设置控制值
TArray<float> ControlValues;
ControlValues.SetNum(RigLogicComp->GetControlValueCount());
ControlValues[0] = 1.0f; // 例如，微笑
ControlValues[1] = 0.5f; // 例如，眨眼
RigLogicComp->SetControlValues(ControlValues);
```

### 进阶用法

可以监听 `OnDNADataLoaded` 委托来确保 DNA 加载完成后再进行操作，或使用 `GetLODIndex` 和 `SetLODIndex` 来动态管理面部动画的细节层次以优化性能。

## Demo 示例

一个最小可运行的 C++ 示例通常包含：
1.  一个继承自 `ACharacter` 的类。
2.  在构造函数中创建并附加 `URigLogicComponent`。
3.  在 `BeginPlay` 中加载 DNA 和设置网格体。
4.  在 `Tick` 或通过输入事件更新控制值。
详细的代码示例请参考各模块文档，特别是 `RigLogicModule` 和 `RigLogicLib` 的文档。

## 模块依赖

要使用 RigLogic 插件，你的模块通常需要依赖 `RigLogicModule`。以下是该插件独特的依赖项：

| 模块 | 用途 |
|---|---|
| `SkeletalMeshUtilitiesCommon` | 处理骨骼网格体相关的通用工具函数。 |
| `RHI` | 渲染硬件接口，用于可能的 GPU 计算加速。 |
| `RenderCore` | 渲染核心模块，支持底层渲染操作。 |
| `MessageLog` | 用于在编辑器中输出日志和错误信息。 |

## 维护状态

### 近期更新

（注：未提供具体的 git log 信息，以下为基于插件规模和来源的推测性描述）
-   作为 Epic Games 官方维护的 MetaHuman 核心组件，该插件会随着引擎版本更新而持续维护。
-   更新通常包含性能优化、新 DNA 特性支持、Bug 修复以及对新平台的适配。

### 维护评价

-   **创建时间**：约 5 年前（2020年），与 MetaHuman 技术的推出时间相符。
-   **维护状态**：**活跃维护中**。作为 Epic Games 官方面部动画解决方案的核心，其维护优先级很高，会随引擎版本定期更新。
-   **已知限制**：主要面向高端面部动画需求，对于简单的卡通角色可能过于复杂。DNA 文件的创建和编辑依赖于特定的 DCC 工具链（如 Maya + 插件）。
-   **推荐使用**：**强烈推荐**用于任何需要 MetaHuman 级别面部动画的项目。它是 Unreal Engine 中实现最真实面部动画的官方和标准方式。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/rig-logic-in-unreal-engine/) （MetaHuman/RigLogic 相关文档）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic/Source/RigLogicLibTest)