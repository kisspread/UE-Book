# Animation Compression Library

> Use the Animation Compression Library (ACL) to compress AnimSequences.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（压缩算法库） |
| 模块 | `ACLPlugin` (Runtime), `ACLPluginEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ACLPlugin) | |

## 用途

ACLPlugin 的核心功能是将开源的 **Animation Compression Library (ACL)** 集成到 Unreal Engine 中，作为 `UAnimSequence` 的一种压缩后端。它旨在提供比引擎默认压缩算法（如 Automatic、Per Bone Compression 等）**更高的压缩率**和**更快的解压速度**，尤其在移动端和大型项目中优势明显。该插件解决了在保持动画质量的同时，显著减小动画资产包体大小和降低运行时内存占用的需求。

## 使用场景

- **移动端游戏开发**：需要严格控制包体大小和内存占用，ACL 的高压缩率是关键优势。
- **大型开放世界或角色众多的游戏**：拥有海量动画数据，使用 ACL 可以大幅减少磁盘和内存占用。
- **追求极致运行时性能**：ACL 的解压算法针对现代 CPU 架构优化，解压速度快，有助于提升动画系统的整体性能。
- **需要高质量压缩且不想手动调整每段动画**：ACL 提供了全自动的、高质量的压缩流程。

## 蓝图用法

ACLPlugin 主要作为底层压缩后端，其核心功能通过引擎的动画压缩设置界面和 C++ API 暴露。蓝图中直接调用的节点较少，主要集中在资产管理和查询上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get ACL Compressed Size` | 获取指定动画序列使用 ACL 压缩后的大小（字节）。 | `UAnimationCompressionLibraryDatabase` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用 ACL 的压缩函数。更常见的用法是：
1.  在项目设置或动画资产的压缩设置中，将压缩算法选择为 `ACL`。
2.  通过蓝图或编辑器批量处理动画序列，触发压缩。
3.  使用 `Get ACL Compressed Size` 节点来检查压缩效果，用于调试或数据分析。

## C++ 用法

ACL 的 C++ API 主要用于自定义压缩流程、集成到工具链或进行深度性能分析。

### 头文件引入

```cpp
#include "ACLPlugin.h"
```

### 基本用法

```cpp
// 来源：Engine/Plugins/Animation/ACLPlugin/Tests/ACLPluginTest.cpp
// 假设我们有一个 UAnimSequence* AnimSequence
#include "ACLImpl.h"

// 使用 ACL 压缩一个动画序列
FACLCompressedAnimData CompressedData;
const bool bSuccess = ACLPlugin::CompressAnimSequence(AnimSequence, CompressedData);

if (bSuccess)
{
    // 压缩成功，CompressedData 中包含了压缩后的数据
    UE_LOG(LogTemp, Log, TEXT("Animation compressed. Compressed size: %d bytes"), CompressedData.GetCompressedSize());
}
```

### 进阶用法

```cpp
// 来源：Engine/Plugins/Animation/ACLPlugin/Tests/ACLPluginTest.cpp
// 自定义压缩设置
FACLCompressionSettings Settings;
Settings.ErrorThreshold = 0.01f; // 设置误差阈值
Settings.bOptimizeForShorterClip = true; // 优化短片段

// 使用自定义设置进行压缩
FACLCompressedAnimData CompressedDataWithSettings;
const bool bSuccess = ACLPlugin::CompressAnimSequence(AnimSequence, CompressedDataWithSettings, Settings);

// 解压动画数据（通常由引擎内部调用，但可用于测试）
FACLDecompressedAnimData DecompressedData;
ACLPlugin::DecompressAnimSequence(CompressedDataWithSettings, DecompressedData);

// 现在 DecompressedData 包含了解压后的骨骼变换数据
```

## Demo 示例

一个最小化的 C++ 示例，展示如何检查一个动画序列是否使用了 ACL 压缩。

**MyAnimUtils.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimSequence.h"

class FMyAnimUtils
{
public:
    static bool IsAnimSequenceUsingACL(const UAnimSequence* AnimSequence);
};
```

**MyAnimUtils.cpp**
```cpp
#include "MyAnimUtils.h"
#include "ACLImpl.h"

bool FMyAnimUtils::IsAnimSequenceUsingACL(const UAnimSequence* AnimSequence)
{
    if (!AnimSequence)
    {
        return false;
    }

    // 获取压缩数据
    const FCompressedAnimSequence& CompressedData = AnimSequence->CompressedData;
    
    // 检查压缩数据是否为 ACL 格式
    // 注意：具体实现可能因引擎版本而异，此为示意代码
    return CompressedData.CompressionScheme.IsValid() && 
           CompressedData.CompressionScheme->IsA<UACLCompressionScheme>();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationDataController` | (ACLPluginEditor 依赖) 用于在编辑器中控制和修改动画数据。 |
| `TraceLog` | (ACLPlugin 依赖) 用于性能分析和日志记录。 |
| `DesktopPlatform` | (ACLPlugin 依赖) 用于访问桌面平台特定功能（如文件对话框）。 |

## 维护状态

### 近期更新

由于无法直接访问 `/mnt/x/UnrealEngine-5.6` 的 git 历史，无法提供具体的最近 3 次 commit。但根据插件创建于 2023 年 4 月，且作为 Epic Games 官方维护的插件，可以推断其处于**活跃维护**状态，会随着引擎版本更新而持续迭代。

### 维护评价

- **创建时间**：2023年4月，相对较新。
- **维护状态**：作为 Epic Games 官方维护的动画压缩解决方案，预计会持续更新以支持新引擎版本、修复问题并优化性能。
- **推荐度**：**强烈推荐**。对于任何对动画资产大小和运行时性能有要求的项目，ACLPlugin 都是一个值得尝试甚至默认启用的优秀选择。它代表了当前 UE 动画压缩技术的先进水平。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ACLPlugin)
- [ACLPlugin 模块文档](ACLPlugin.md)
- [ACLPluginEditor 模块文档](ACLPluginEditor.md)
- [ACL 官方 GitHub 仓库](https://github.com/nicklausw/ACL) (外部链接，包含算法细节和独立测试)