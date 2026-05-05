# Animation Compression Library

> Use the Animation Compression Library (ACL) to compress AnimSequences.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（动画压缩数据库资产） |
| 模块 | `ACLPlugin` (Runtime), `ACLPluginEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ACLPlugin) | |

## 用途

ACLPlugin 的核心功能是将 Unreal Engine 的动画序列（`UAnimSequence`）压缩任务交由 **Animation Compression Library (ACL)** 处理，以替代或补充引擎内置的压缩方案。ACL 是一个专注于高性能、高保真度的动画压缩库，其压缩率和解压速度通常优于 UE 默认的压缩算法。

该插件解决的核心问题是：**如何在保持动画质量的前提下，显著减少动画数据的内存占用和加载时间**。这对于内存敏感的平台（如移动端、VR）或拥有海量动画资产的大型项目至关重要。它通过提供一个更先进的压缩后端，让开发者能够无缝地优化项目的动画资源。

## 使用场景

-   **移动端游戏开发**：内存和包体大小是关键限制，使用 ACL 压缩可以大幅减少动画资源占用。
-   **VR/AR 应用**：对帧率和内存带宽要求极高，ACL 的快速解压特性有助于维持流畅体验。
-   **拥有大量动画资产的项目**：如开放世界游戏、MMO，通过 ACL 压缩可以节省数 GB 的内存和磁盘空间。
-   **追求更高压缩质量**：当 UE 默认压缩算法在特定动画上产生明显瑕疵时，可以尝试 ACL 作为替代方案。
-   **需要批量处理和统计分析**：利用插件提供的 Commandlet 工具，可以自动化压缩流程并导出详细的压缩质量报告。

## 蓝图用法

ACLPlugin 主要通过编辑器工具和资产属性进行配置，直接暴露给蓝图的可调用函数较少，核心操作集中在编辑器和命令行工具中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CompressAnimationSequence` | 使用当前项目设置的压缩编解码器（可能是 ACL）压缩指定的动画序列。 | `UAnimationLibrary` |
| `UpdateAnimationCompressionLibraryDatabase` | 更新指定的 ACL 数据库资产，重新构建其内部映射。 | `UAnimationCompressionLibraryDatabase` |

### 使用示例（蓝图描述）

1.  **在编辑器中压缩单个动画**：
    *   在内容浏览器中右键点击一个 `UAnimSequence` 资产。
    *   选择 `Asset Actions` -> `Compress`。
    *   在弹出的窗口中，确保 `Bone Compression Settings` 设置为使用了 ACL 编解码器的预设（例如 `DefaultBoneCompressionSettings` 或自定义的 ACL 设置）。
    *   点击 `Apply` 即可触发压缩。

2.  **通过蓝图批量压缩**：
    *   使用 `Get All Assets Of Class` 节点获取所有 `AnimSequence` 资产。
    *   遍历数组，对每个资产调用 `CompressAnimationSequence` 节点。
    *   该节点会使用项目设置中指定的默认压缩设置进行压缩。

## C++ 用法

ACL 的 C++ 用法主要涉及配置压缩编解码器和使用数据库。

### 头文件引入

```cpp
#include "ACLPlugin.h"
#include "AnimBoneCompressionCodec_ACL.h"
#include "AnimationCompressionLibraryDatabase.h"
```

### 基本用法

设置一个使用 ACL 的骨骼压缩设置资产。

```cpp
// 假设你已经有了一个 UAnimBoneCompressionSettings 资产的引用 (BoneCompressionSettings)
// 在编辑器中或通过代码创建一个 ACL 编解码器实例
UAnimBoneCompressionCodec_ACL* ACLCodec = NewObject<UAnimBoneCompressionCodec_ACL>(BoneCompressionSettings);
ACLCodec->AddToRoot(); // 防止被垃圾回收，通常资产会管理其生命周期

// 配置 ACL 编解码器的参数（可选）
ACLCodec->ErrorThreshold = 0.01f; // 设置容错阈值
ACLCodec->CompressionLevel = ACLCompressionLevel::Medium; // 设置压缩级别

// 将 ACL 编解码器添加到压缩设置中
BoneCompressionSettings->Codecs.Add(ACLCodec);
```

### 进阶用法

使用 `UAnimationCompressionLibraryDatabase` 来管理大量动画的压缩数据，适用于需要流式加载或共享压缩数据的场景。

```cpp
// 1. 创建或获取一个 ACL 数据库资产
UAnimationCompressionLibraryDatabase* ACLDatabase = LoadObject<UAnimationCompressionLibraryDatabase>(nullptr, TEXT("/Game/Animation/ACLDatabase"));

// 2. 将动画序列添加到数据库中进行管理
// 通常在编辑器中通过资产属性面板操作，或通过命令行工具批量添加。

// 3. 在运行时，确保数据库已加载并激活
if (ACLDatabase)
{
    // 数据库通常在启动时自动加载，但可以手动检查其状态
    if (!ACLDatabase->IsReadyForUse())
    {
        // 等待加载完成或处理错误
    }
}

// 4. 当动画序列被设置为使用该数据库时，引擎会自动从数据库中读取压缩数据
// 无需在 C++ 中直接调用解压函数，动画系统会透明处理。
```

## Demo 示例

以下示例展示了如何在 C++ 中创建一个使用 ACL 压缩的动画序列。

**MyAnimCompressionExample.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyAnimCompressionExample.generated.h"

class UAnimSequence;
class UAnimBoneCompressionSettings;

UCLASS(BlueprintType)
class UMyAnimCompressionExample : public UObject
{
    GENERATED_BODY()

public:
    /** 使用 ACL 压缩一个动画序列 */
    UFUNCTION(BlueprintCallable, Category = "Animation Compression")
    static bool CompressAnimSequenceWithACL(UAnimSequence* AnimSequence);

private:
    /** 获取或创建默认的 ACL 压缩设置 */
    static UAnimBoneCompressionSettings* GetDefaultACLCompressionSettings();
};
```

**MyAnimCompressionExample.cpp**
```cpp
#include "MyAnimCompressionExample.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimBoneCompressionSettings.h"
#include "AnimBoneCompressionCodec_ACL.h"

bool UMyAnimCompressionExample::CompressAnimSequenceWithACL(UAnimSequence* AnimSequence)
{
    if (!AnimSequence)
    {
        return false;
    }

    UAnimBoneCompressionSettings* CompressionSettings = GetDefaultACLCompressionSettings();
    if (!CompressionSettings)
    {
        return false;
    }

    // 设置动画序列的压缩设置
    AnimSequence->BoneCompressionSettings = CompressionSettings;

    // 触发压缩
    // 注意：在编辑器中，这通常会异步执行。在运行时调用需谨慎。
    AnimSequence->RequestAnimCompression(FRequestAnimCompressionParams());

    return true;
}

UAnimBoneCompressionSettings* UMyAnimCompressionExample::GetDefaultACLCompressionSettings()
{
    // 尝试加载项目设置中定义的默认骨骼压缩设置
    // 这里假设项目已经配置了使用 ACL 的设置
    UAnimBoneCompressionSettings* Settings = LoadObject<UAnimBoneCompressionSettings>(
        nullptr,
        TEXT("/Engine/Animation/DefaultBoneCompressionSettings") // 或项目自定义路径
    );

    // 如果需要动态创建，可以在此处添加逻辑
    // 但通常建议在编辑器中预先配置好压缩设置资产。

    return Settings;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ACLPlugin` | ACL 压缩库的核心运行时模块，提供压缩和解压功能。 |
| `AnimationDataController` | 用于在编辑器中安全地修改动画资产数据。 |
| `TraceLog` | 用于记录 ACL 压缩过程中的性能跟踪和日志信息。 |
| `DesktopPlatform` | 用于访问桌面平台特定功能，可能用于文件对话框或路径处理。 |

## 维护状态

### 近期更新

```
- 2025-10-03 834d550a1503 修复了在不完全支持 C++20 的平台上使用 ACLPlugin 时的编译问题。
- 2025-09-15 44e4da079004 [AutoRTFM] 在 ACLPlugin 中使用 FMemory::Malloc 代替 GMalloc。
- 2025-08-20 7e2e75baa70e 压缩动画的线程安全性和确定性改进：废弃了 UAnimSequence::CompressedData 的公共访问和编辑器时用法；引入了读写锁和驻留 API 等。
```

### 维护评价

ACLPlugin 是一个**活跃维护中**的核心动画优化插件。

-   **年龄**：创建于 2023 年，相对年轻，但已集成到 UE 主线。
-   **更新频率**：近期（2025年）有多次重要更新，主要集中在**编译兼容性、内存安全性和线程安全**方面，表明 Epic 和社区（Nicholas Frechette）在持续投入。
-   **功能状态**：功能稳定，是 UE 动画压缩的官方推荐方案之一。近期更新主要针对底层稳定性和与新引擎特性（如 AutoRTFM）的兼容，而非新增功能。
-   **已知限制**：作为高性能库，其压缩/解压行为需要与 UE 的动画系统深度集成，更新时需注意与引擎版本的匹配。
-   **推荐使用**：**强烈推荐**。对于任何关注动画内存和性能的项目，ACLPlugin 都是首选工具。它已被 Epic 官方认可并集成，维护可靠，性能收益显著。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ACLPlugin)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/animation-compression-library-plugin-in-unreal-engine/) (UE 官方文档链接)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ACLPlugin/Tests) (如果存在)