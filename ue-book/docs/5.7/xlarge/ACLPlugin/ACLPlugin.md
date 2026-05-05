# Animation Compression Library

> Use the Animation Compression Library (ACL) to compress AnimSequences.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `ACLPlugin` (Runtime), `ACLPluginEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ACLPlugin) | |

## 用途

ACLPlugin 是一个高性能的动画压缩插件，它集成了开源的 Animation Compression Library (ACL)。该插件旨在解决 Unreal Engine 内置动画压缩算法在压缩率、解压速度和内存占用方面的局限性。ACL 通过更先进的算法，能够在保持动画质量的同时，显著减小动画序列的内存占用，并提高运行时解压性能。它特别适用于需要处理大量动画数据的项目，如大型开放世界游戏或角色众多的游戏。

## 使用场景

- **大型开放世界游戏**：拥有海量动画数据，需要极致的压缩率来减少内存和磁盘占用。
- **移动平台开发**：对内存和带宽敏感，需要高效的动画压缩方案。
- **需要流式加载动画**：ACL 的数据库功能支持将动画数据分层并按需流式加载，优化内存使用。
- **追求高保真动画**：ACL 的“Safe”模式可以在几乎无损的情况下压缩动画，适用于过场动画等关键场景。
- **需要精细控制压缩质量**：ACL 提供了多种压缩级别和可配置参数，允许开发者在压缩率、质量和速度之间进行权衡。

## 蓝图用法

ACLPlugin 主要提供动画压缩编解码器，这些编解码器在动画资产的属性面板中配置，而非直接在蓝图中调用。其运行时蓝图交互主要集中在 `UAnimationCompressionLibraryDatabase` 资产上，用于控制动画数据库的视觉保真度。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Visual Fidelity` | 异步请求更改动画数据库的视觉保真度（最高/中等/最低）。 | `UAnimationCompressionLibraryDatabase` |
| `Get Visual Fidelity` | 获取当前动画数据库的视觉保真度。 | `UAnimationCompressionLibraryDatabase` |

### 使用示例（蓝图描述）

1.  **配置压缩编解码器**：在 `AnimSequence` 资产的 `Compression` 设置中，将 `Bone Compression Codec` 设置为 `Anim Compress ACL` 或 `Anim Compress ACL Safe` 等 ACL 编解码器。
2.  **使用数据库流式加载**：
    *   创建一个 `AnimationCompressionLibraryDatabase` 资产。
    *   在需要使用数据库的 ACL 编解码器（如 `Anim Compress ACL Database`）中，将 `Database Asset` 属性指向该数据库资产。
    *   在蓝图中，获取该数据库资产的引用，调用 `Set Visual Fidelity` 节点，并传入 `ACLVisualFidelity` 枚举值（如 `Highest`）来请求加载最高质量的动画数据。该操作是异步的，可以通过 `ACLVisualFidelityChangeResult` 枚举检查结果。

## C++ 用法

ACLPlugin 的核心是提供一系列 `UAnimBoneCompressionCodec` 和 `UAnimCurveCompressionCodec` 的子类，用于替换或增强引擎默认的压缩行为。通常，开发者通过配置资产来使用它们，而不是直接在代码中实例化。

### 头文件引入

```cpp
#include "AnimBoneCompressionCodec_ACL.h"
#include "AnimBoneCompressionCodec_ACLSafe.h"
#include "AnimBoneCompressionCodec_ACLDatabase.h"
#include "AnimCurveCompressionCodec_ACL.h"
#include "AnimationCompressionLibraryDatabase.h"
```

### 基本用法

在 C++ 中，你通常不会直接创建这些编解码器对象，而是通过配置动画序列或项目设置来使用它们。以下示例展示了如何通过代码查询或设置动画序列的压缩编解码器（通常在编辑器工具或自定义管线中）。

```cpp
// 假设你有一个 UAnimSequence* AnimSeq
// 获取当前的骨骼压缩编解码器
UAnimBoneCompressionCodec* BoneCodec = AnimSeq->BoneCompressionCodec;
if (BoneCodec)
{
    // 检查是否是 ACL 编解码器
    if (UAnimBoneCompressionCodec_ACL* ACLCodec = Cast<UAnimBoneCompressionCodec_ACL>(BoneCodec))
    {
        UE_LOG(LogTemp, Log, TEXT("AnimSequence uses ACL compression."));
        // 可以访问 ACLCodec 的属性，例如 CompressionLevel, ErrorThreshold 等
    }
}

// 设置一个新的 ACL 编解码器 (通常在编辑器工具中)
UAnimBoneCompressionCodec_ACL* NewACLCodec = NewObject<UAnimBoneCompressionCodec_ACL>(GetTransientPackage());
NewACLCodec->CompressionLevel = ACLCompressionLevel::Medium;
NewACLCodec->ErrorThreshold = 0.01f;
AnimSeq->BoneCompressionCodec = NewACLCodec;
// 注意：修改后通常需要重新压缩动画序列
```

### 进阶用法：与动画数据库交互

ACL 数据库功能允许将动画数据分层存储和流式加载。以下代码展示了如何在运行时通过 C++ 控制数据库的视觉保真度。

```cpp
// 假设你有一个 UAnimationCompressionLibraryDatabase* DatabaseAsset
// 请求将视觉保真度切换到“最高”
ACLVisualFidelity DesiredFidelity = ACLVisualFidelity::Highest;
ACLVisualFidelityChangeResult Result = DatabaseAsset->SetVisualFidelity(DesiredFidelity);

switch (Result)
{
case ACLVisualFidelityChangeResult::Dispatched:
    UE_LOG(LogTemp, Log, TEXT("Fidelity change request dispatched."));
    break;
case ACLVisualFidelityChangeResult::Completed:
    UE_LOG(LogTemp, Log, TEXT("Fidelity change completed immediately."));
    break;
case ACLVisualFidelityChangeResult::Failed:
    UE_LOG(LogTemp, Warning, TEXT("Fidelity change failed."));
    break;
}

// 你也可以使用异步版本，通过委托接收结果
FOnVisualFidelityChangeCompleted OnCompleted;
OnCompleted.BindLambda([](ACLVisualFidelity NewFidelity){
    UE_LOG(LogTemp, Log, TEXT("Visual fidelity changed to: %d"), static_cast<int32>(NewFidelity));
});
DatabaseAsset->SetVisualFidelityAsync(DesiredFidelity, OnCompleted);
```

## Demo 示例

以下是一个最小的 C++ 示例，展示如何创建一个使用 ACL 压缩的动画序列（通常在编辑器模块或命令行工具中）。

**MyAnimCompressionTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyAnimCompressionTool.generated.h"

class UAnimSequence;
class UAnimBoneCompressionCodec_ACL;

UCLASS()
class UMyAnimCompressionTool : public UObject
{
    GENERATED_BODY()

public:
    /** 使用 ACL Safe 编解码器压缩指定的动画序列 */
    UFUNCTION(BlueprintCallable, Category = "Animation|ACL")
    static bool CompressAnimSequenceWithACLSafe(UAnimSequence* AnimSequence);

private:
    /** 创建并配置一个 ACL Safe 编解码器实例 */
    static UAnimBoneCompressionCodec_ACL* CreateACLSafeCodec();
};
```

**MyAnimCompressionTool.cpp**
```cpp
#include "MyAnimCompressionTool.h"
#include "AnimSequence.h"
#include "AnimBoneCompressionCodec_ACLSafe.h"

bool UMyAnimCompressionTool::CompressAnimSequenceWithACLSafe(UAnimSequence* AnimSequence)
{
    if (!AnimSequence)
    {
        return false;
    }

    // 创建 ACL Safe 编解码器
    UAnimBoneCompressionCodec_ACLSafe* ACLSafeCodec = CreateACLSafeCodec();
    if (!ACLSafeCodec)
    {
        return false;
    }

    // 设置动画序列的压缩编解码器
    AnimSequence->BoneCompressionCodec = ACLSafeCodec;

    // 触发动画序列重新压缩 (这通常需要在编辑器环境中进行)
    // AnimSequence->RequestAnimCompression(...); // 具体API取决于引擎版本和上下文

    UE_LOG(LogTemp, Log, TEXT("AnimSequence '%s' configured for ACL Safe compression."), *AnimSequence->GetName());
    return true;
}

UAnimBoneCompressionCodec_ACLSafe* UMyAnimCompressionTool::CreateACLSafeCodec()
{
    UAnimBoneCompressionCodec_ACLSafe* Codec = NewObject<UAnimBoneCompressionCodec_ACLSafe>(GetTransientPackage());
    // ACL Safe 编解码器使用预设的安全设置，通常不需要额外配置
    // 你可以在这里覆盖一些基础属性，例如 ErrorThreshold
    // Codec->ErrorThreshold = 0.0f; // Safe 模式默认误差阈值很低
    return Codec;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TraceLog` | 用于 ACL 库内部的性能追踪和日志记录。 |
| `DesktopPlatform` | 用于访问桌面平台特定功能（可能用于文件对话框等编辑器功能）。 |
| `AnimationDataController` | (ACLPluginEditor 依赖) 用于在编辑器中控制和修改动画数据。 |

## 维护状态

### 近期更新

```
- 2025-10-03 ce6ff392ddca 修复 FTSTicker::RemoveTicker 使用中“忽略返回值”的 nodiscard 警告。
- 2025-10-03 2415c7aa20ad 修复在使用 Clang 20 构建时出现的两种 nodiscard 警告。
- 2025-10-03 ec9009980d52 为具有对应 .gen.cpp 文件的源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME。
```

### 维护评价

ACLPlugin 是一个相对较新的插件（创建于 2023 年），目前处于**活跃维护**状态。最近的提交（2025年10月）主要是针对编译器警告的修复，表明 Epic Games 持续关注其代码质量和与最新工具链的兼容性。该插件功能稳定，是 UE5 动画压缩管线的重要组成部分，**推荐在新项目中使用**，特别是那些对动画内存和性能有较高要求的项目。由于其基于成熟的开源 ACL 库，且由 Epic 官方维护，可靠性较高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ACLPlugin)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ACLPlugin/Tests)