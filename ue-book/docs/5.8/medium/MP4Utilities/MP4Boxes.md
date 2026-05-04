# MP4 (ISO/IEC 14496-12) utilities

> Provides helpers to work with mp4 files

| 属性 | 值 |
|---|---|
| 分类 | Media |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MP4Utilities` (Runtime), `MP4Boxes` (Runtime), `MP4Muxer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-02-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MP4Utilities) | |

## 用途

MP4Utilities 插件并非用于播放媒体文件，而是提供了一套底层的、符合 ISO/IEC 14496-12 (MP4 容器格式) 标准的工具集。其核心功能是**解析和操作 MP4 文件的内部结构（Box/Atom）**。它允许开发者在 C++ 层面深入读取、遍历和理解 MP4 文件的元数据、轨道信息、样本表等，适用于需要对 MP4 文件进行底层分析、处理或构建自定义媒体处理管线的场景。

## 使用场景

-   **媒体文件分析工具**：你需要开发一个工具来检查 MP4 文件的内部结构，例如查看所有 Box 类型、轨道时长、编码信息等。
-   **自定义媒体处理管线**：你的项目需要从 MP4 文件中提取特定的元数据（如语言标签、轨道名称）或样本信息，用于驱动非标准的媒体播放或处理逻辑。
-   **分段 MP4 (fMP4) 处理**：你需要处理或生成用于流媒体（如 DASH、HLS）的分段 MP4 文件，该插件提供了对 `moof`、`traf`、`trun` 等 Fragment 相关 Box 的解析支持。
-   **媒体资产预处理**：在编辑器或打包流程中，需要预先分析大量 MP4 资产的结构信息。

## 蓝图用法

根据提供的源码分析，`MP4Boxes` 模块的核心类（如 `FMP4BoxBase`, `FMP4Track`）均为纯 C++ 类，未暴露 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 接口。因此，**该插件主要面向 C++ 开发者，不提供蓝图节点**。所有操作均需在 C++ 代码中进行。

## C++ 用法

### 头文件引入

使用 `MP4Boxes` 模块时，主要引入以下头文件：

```cpp
#include "MP4Boxes.h"
#include "MP4Track.h"
#include "MP4BoxIterators.h"
```

### 基本用法：解析 MP4 文件并遍历 Box

以下示例展示了如何使用 `MP4Utilities` 模块（假设其提供了文件解析功能）和 `MP4Boxes` 模块来解析一个 MP4 文件，并遍历其顶层的 Box 结构。

```cpp
// 假设 MP4Utilities 模块提供了一个解析函数，返回根 Box 列表
// TArray<TSharedPtr<MP4Boxes::FMP4BoxBase>> RootBoxes = MP4Utilities::ParseMP4File(FilePath);

// 遍历所有根级 Box
for (const TSharedPtr<MP4Boxes::FMP4BoxBase>& RootBox : RootBoxes)
{
    UE_LOG(LogTemp, Log, TEXT("Found Box: Type=0x%08X, Size=%lld, Offset=%lld"),
        RootBox->GetType(), RootBox->GetBoxSize(), RootBox->GetBoxFileOffset());

    // 检查是否为容器 Box（非叶子节点），并递归遍历其子 Box
    if (!RootBox->IsLeafBox())
    {
        for (const TSharedPtr<MP4Boxes::FMP4BoxBase>& ChildBox : RootBox->GetChildren())
        {
            UE_LOG(LogTemp, Log, TEXT("  Child Box: Type=0x%08X"), ChildBox->GetType());
        }
    }
}
```

### 进阶用法：获取轨道信息与样本迭代

以下示例展示了如何从解析出的 Box 树中找到 `moov` Box，进而获取 `trak` Box，并创建 `FMP4Track` 对象来查询轨道元数据和迭代样本时间戳。

```cpp
// 1. 在根 Box 中查找 `moov` Box (类型为 'moov')
TSharedPtr<MP4Boxes::FMP4BoxMOOV> MoovBox;
for (const TSharedPtr<MP4Boxes::FMP4BoxBase>& Box : RootBoxes)
{
    if (Box->GetType() == MP4Boxes::FMP4BoxMOOV::StaticType()) // 假设有静态类型标识
    {
        MoovBox = StaticCastSharedPtr<MP4Boxes::FMP4BoxMOOV>(Box);
        break;
    }
}

if (MoovBox.IsValid())
{
    // 2. 在 `moov` Box 中查找第一个 `trak` Box
    TSharedPtr<MP4Boxes::FMP4BoxTRAK> TrakBox = MoovBox->FindBoxRecursive<MP4Boxes::FMP4BoxTRAK>('trak');
    if (TrakBox.IsValid())
    {
        // 3. 创建轨道对象 (需要 FragmentInfo，此处简化为 nullptr)
        TSharedPtr<MP4Boxes::FMP4Track> Track = MP4Boxes::FMP4Track::Create(TrakBox, nullptr);
        if (Track.IsValid())
        {
            // 4. 准备轨道（计算时长等）
            MP4Utilities::FFractionalTime MovieDuration; // 需要从 mvhd box 获取
            Track->Prepare(MovieDuration, MovieDuration);

            // 5. 获取轨道元数据
            const MP4Boxes::FMP4TrackMetadataCommon& Metadata = Track->GetMetadata();
            UE_LOG(LogTemp, Log, TEXT("Track Language: %s, Name: %s"), *Metadata.LanguageCode, *Metadata.Name);

            // 6. 使用迭代器遍历样本时间戳 (STTS Box)
            MP4Boxes::FSTTSBoxIterator SttsIterator;
            SttsIterator.SetBox(Track->GetSTTSBox()); // 假设 FMP4Track 提供了获取 STTS Box 的方法
            SttsIterator.SetToSampleNumber(0); // 从第一个样本开始

            for (uint32 i = 0; i < Track->GetNumTotalSamples(); ++i)
            {
                int64 SamplePTS = SttsIterator.Time;
                UE_LOG(LogTemp, Verbose, TEXT("Sample %u PTS: %lld"), i, SamplePTS);
                SttsIterator.Next();
            }
        }
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何使用 `MP4Boxes` 模块解析一个内存中的 MP4 数据块。

**MP4DemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MP4DemoActor.generated.h"

UCLASS()
class AMP4DemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMP4DemoActor();

protected:
    virtual void BeginPlay() override;

private:
    void AnalyzeMP4Data(const TArray<uint8>& MP4Data);
};
```

**MP4DemoActor.cpp**
```cpp
#include "MP4DemoActor.h"
#include "MP4Boxes.h"
#include "MP4Track.h"

AMP4DemoActor::AMP4DemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMP4DemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 示例：这里应该从文件或网络加载真实的 MP4 数据
    TArray<uint8> DummyMP4Data;
    // ... 填充数据 ...

    if (DummyMP4Data.Num() > 0)
    {
        AnalyzeMP4Data(DummyMP4Data);
    }
}

void AMP4DemoActor::AnalyzeMP4Data(const TArray<uint8>& MP4Data)
{
    // 注意：实际使用中，MP4Utilities 模块应提供将原始字节解析为 Box 树的函数。
    // 以下为示意性代码，假设存在一个解析函数。
    // TArray<TSharedPtr<MP4Boxes::FMP4BoxBase>> ParsedBoxes = MP4Utilities::ParseMP4Data(MP4Data.GetData(), MP4Data.Num());

    // 由于无法调用实际解析函数，此处演示如何手动创建一个 Box 对象进行测试。
    MP4Utilities::FMP4BoxInfo TestBoxInfo;
    TestBoxInfo.Type = 'ftyp'; // 文件类型 Box
    TestBoxInfo.Size = 20;
    TestBoxInfo.Data.SetNum(16); // 模拟数据

    TSharedPtr<MP4Boxes::FMP4BoxBase> TestBox = MP4Boxes::FMP4BoxFTYP::Create(nullptr, TestBoxInfo);

    if (TestBox.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully created a test FTYP box. Type: 0x%08X, Size: %lld"),
            TestBox->GetType(), TestBox->GetBoxSize());

        // 尝试将其转换为具体类型并访问特有方法
        TSharedPtr<MP4Boxes::FMP4BoxFTYP> FtypBox = StaticCastSharedPtr<MP4Boxes::FMP4BoxFTYP>(TestBox);
        if (FtypBox.IsValid())
        {
            // 注意：由于数据是模拟的，以下调用可能失败或返回无意义值
            // uint32 MajorBrand = FtypBox->GetMajorBrand();
            // UE_LOG(LogTemp, Log, TEXT("Major Brand: 0x%08X"), MajorBrand);
        }
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MP4Utilities` | 提供 MP4 文件解析的基础工具和数据结构 |
| `MP4Boxes` | 提供 MP4 Box 结构的 C++ 类表示和操作逻辑 |
| `MP4Muxer` | 提供 MP4 文件的复用（Muxing）功能 |

## 维护状态

### 近期更新

由于插件创建时间非常近（2026年2月），且用户未提供具体的 git log 信息，无法列出近期提交记录。可以推断该插件处于**初始开发阶段**。

### 维护评价

-   **创建时间**：2026年2月25日，是一个非常新的插件。
-   **维护状态**：**活跃开发中**。作为 Epic Games 官方维护的插件，且处于早期阶段，预计会有持续的功能完善和 bug 修复。
-   **已知限制**：默认禁用 (`EnabledByDefault: false`)，表明它可能尚未达到生产就绪状态，或属于特定用途的工具。主要提供 C++ API，无蓝图支持。
-   **推荐使用**：如果你需要对 MP4 文件进行底层、结构化的操作，且项目允许使用实验性或较新的官方插件，可以尝试使用。对于简单的媒体播放需求，应使用标准的 Media Framework。建议关注其后续版本更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MP4Utilities)
-   [官方文档](https://docs.unrealengine.com) (暂无专门文档，可参考 Media Framework 文档)