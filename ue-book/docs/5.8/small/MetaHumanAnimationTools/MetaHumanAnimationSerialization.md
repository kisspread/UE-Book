# MetaHuman Animation Tools

> Tooling for working with MetaHuman Animation data.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画数据资产） |
| 模块 | `MetaHumanAnimationSerialization` (Runtime), `MetaHumanAnimationSerializationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2026-02-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimationTools) | |

## 用途

MetaHumanAnimationTools 提供了一套针对 MetaHuman 面部动画曲线数据的高效序列化框架。它解决的核心问题是：如何以紧凑的二进制格式存储和读取大量的面部动画曲线数据（blendshape curves），同时支持可配置的精度和压缩策略。

该插件包含两个关键能力：

1. **精度控制**：支持 Float（全精度）、Int16（16 位整数量化）、Int10（10 位整数量化）三种精度级别，允许在文件大小和动画质量之间做权衡。
2. **稀疏压缩**：通过 `Sparse` 压缩模式，仅记录发生变化的曲线值（基于阈值判断），大幅减少冗余数据写入，同时定期写入完整帧以保证解码容错性。

该插件被标记为 `Hidden` 且默认不启用，说明它主要作为 MetaHuman 工具链的内部基础设施，供其他 MetaHuman 插件（如 MetaHuman Creator 集成、LiveLink 面部捕捉等）调用，而非直接面向终端用户。

## 使用场景

- 你正在开发 MetaHuman 面部动画的导入/导出管线 → 使用此插件的编码器/解码器序列化动画曲线数据
- 你需要将实时面部捕捉数据以紧凑格式录制到磁盘 → 使用 Sparse 压缩 + Int10 精度以最小化文件体积
- 你需要在运行时回放预录制的 MetaHuman 面部动画 → 使用解码器逐帧读取曲线数据
- 你正在构建自定义的动画资产格式 → 基于此插件的 FArchive 接口扩展自己的序列化逻辑

## 蓝图用法

该插件的核心类 `FMetaHumanAnimationSerialization` 是纯 C++ 类（非 UObject），不包含任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 标记。因此**不提供蓝图节点**。

如需在蓝图中使用，需自行封装 UObject 包装类。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanAnimationSerialization.h"
```

### 基本用法 — 编码动画数据

将动画曲线序列化写入 FArchive：

```cpp
#include "MetaHumanAnimationSerialization.h"
#include "Serialization/MemoryWriter.h"

// 准备数据
TArray<float> Curves = { 0.5f, 0.3f, 0.8f, 0.1f }; // 面部 blendshape 曲线值
float Time = 1.0f / 30.0f; // 当前帧时间（30fps）

// 创建内存写入器
TArray<uint8> Buffer;
FMemoryWriter Ar(Buffer);

// 初始化编码器：使用 Int16 精度 + 稀疏压缩
FMetaHumanAnimationSerialization Serializer;
Serializer.SetupEncoder(
    Ar,
    FMetaHumanAnimationSerialization::EMaxPrecisionType::Int16,
    FMetaHumanAnimationSerialization::ECompressionMethod::Sparse
);

// 逐帧编码（循环调用 Encode）
for (int32 Frame = 0; Frame < 100; ++Frame)
{
    float FrameTime = Frame / 30.0f;
    // 更新 Curves 数据...
    Serializer.Encode(Ar, FrameTime, Curves);
}
```

### 基本用法 — 解码动画数据

从 FArchive 读取并还原动画曲线：

```cpp
#include "MetaHumanAnimationSerialization.h"
#include "Serialization/MemoryReader.h"

// 假设 Buffer 已包含编码后的数据
FMemoryReader Ar(Buffer);

FMetaHumanAnimationSerialization Deserializer;
Deserializer.SetupDecoder(Ar);

// 逐帧解码
float Time;
TArray<float> Curves;
while (Deserializer.Decode(Ar, Time, Curves))
{
    // 使用 Time 和 Curves 驱动面部动画
    // Time: 当前帧时间戳
    // Curves: 各 blendshape 的权重值
    ApplyFacialPose(Time, Curves);
}
```

### 进阶用法 — 精度与压缩策略选择

```cpp
// 场景 1：高质量离线渲染 — 全精度，无压缩
Serializer.SetupEncoder(
    Ar,
    FMetaHumanAnimationSerialization::EMaxPrecisionType::Float,
    FMetaHumanAnimationSerialization::ECompressionMethod::None
);

// 场景 2：实时预览 — 中等精度，稀疏压缩
Serializer.SetupEncoder(
    Ar,
    FMetaHumanAnimationSerialization::EMaxPrecisionType::Int16,
    FMetaHumanAnimationSerialization::ECompressionMethod::Sparse
);

// 场景 3：网络传输/移动端 — 最低精度，稀疏压缩
Serializer.SetupEncoder(
    Ar,
    FMetaHumanAnimationSerialization::EMaxPrecisionType::Int10,
    FMetaHumanAnimationSerialization::ECompressionMethod::Sparse
);

// 查询当前配置
FMetaHumanAnimationSerialization::EMaxPrecisionType Precision = Serializer.GetMaxPrecisionType();
FMetaHumanAnimationSerialization::ECompressionMethod Method = Serializer.GetCompressionMethod();
```

## Demo 示例

一个完整的最小示例，演示编码后立即解码验证数据一致性：

```cpp
// MetaHumanAnimSerializationExample.h
#pragma once

#include "CoreMinimal.h"

class FMetaHumanAnimSerializationExample
{
public:
    static void RunExample();
};
```

```cpp
// MetaHumanAnimSerializationExample.cpp
#include "MetaHumanAnimSerializationExample.h"
#include "MetaHumanAnimationSerialization.h"
#include "Serialization/MemoryWriter.h"
#include "Serialization/MemoryReader.h"

void FMetaHumanAnimSerializationExample::RunExample()
{
    using namespace std;

    // === 编码阶段 ===
    TArray<uint8> Buffer;
    FMemoryWriter Writer(Buffer);

    FMetaHumanAnimationSerialization Encoder;
    Encoder.SetupEncoder(
        Writer,
        FMetaHumanAnimationSerialization::EMaxPrecisionType::Int16,
        FMetaHumanAnimationSerialization::ECompressionMethod::Sparse
    );

    // 模拟 3 帧动画数据（4 条 blendshape 曲线）
    const int32 NumFrames = 3;
    const int32 NumCurves = 4;

    for (int32 Frame = 0; Frame < NumFrames; ++Frame)
    {
        float Time = Frame / 30.0f;
        TArray<float> Curves;
        Curves.SetNum(NumCurves);

        for (int32 i = 0; i < NumCurves; ++i)
        {
            Curves[i] = FMath::Sin(Time * (i + 1)) * 0.5f + 0.5f;
        }

        Encoder.Encode(Writer, Time, Curves);
    }

    // === 解码阶段 ===
    FMemoryReader Reader(Buffer);

    FMetaHumanAnimationSerialization Decoder;
    Decoder.SetupDecoder(Reader);

    float DecodedTime;
    TArray<float> DecodedCurves;

    int32 FrameIndex = 0;
    while (Decoder.Decode(Reader, DecodedTime, DecodedCurves))
    {
        UE_LOG(LogTemp, Log, TEXT("Frame %d: Time=%.4f, Curves=[%.3f, %.3f, %.3f, %.3f]"),
            FrameIndex, DecodedTime,
            DecodedCurves[0], DecodedCurves[1],
            DecodedCurves[2], DecodedCurves[3]);
        ++FrameIndex;
    }

    UE_LOG(LogTemp, Log, TEXT("Total decoded frames: %d"), FrameIndex);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等基础模块）。核心类仅使用 `FArchive`、`TArray`、`FString` 等基础类型。

## 维护状态

### 近期更新

- 2026-02-03 `f39fc2f9` Correct filename misspelling
- 2026-02-02 `b1aae96f` Add new plugin to efficiently serialize facial animation curve data

### 维护评价

- **创建时间**：2026-02-02，属于全新插件
- **状态**：标记为 `Hidden` 且 `EnabledByDefault=false`，表明这是 MetaHuman 工具链的内部组件
- **代码规模**：仅 5 个源文件，属于小型插件，API 表面简洁清晰
- **设计质量**：接口设计合理，编码器/解码器分离，支持可配置的精度和压缩策略
- **推荐使用**：如果你在开发 MetaHuman 相关的动画管线，推荐使用；如果是通用动画序列化需求，该插件专为面部曲线优化，不一定适合其他场景

⚠️ 该插件为 MetaHuman 生态内部工具，API 可能随 MetaHuman 工具链更新而变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimationTools)