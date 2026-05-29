# Animation Compression Library

> Use the Animation Compression Library (ACL) to compress AnimSequences.

| 属性 | 值 |
|---|---|
| 中文名 | 动画压缩库 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（压缩配置、编解码器预设） |
| 模块 | `ACLPlugin` (Runtime), `ACLPluginEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ACLPlugin) | |

## 用途

ACLPlugin 将开源的 [Animation Compression Library (ACL)](https://github.com/nicholasfrechette/acl) 集成到 Unreal Engine 中，作为骨骼动画压缩的替代编解码器。它解决了 UE 默认动画压缩算法在压缩率与精度之间难以兼顾的问题——ACL 在保持极低解压误差的同时，能将动画数据压缩到远小于默认方案的体积。

核心功能包括：
- **骨骼动画压缩**：提供多种预设编解码器（安全、标准、自定义、数据库），覆盖从最高保真到最大压缩率的全部场景
- **动画曲线压缩**：对动画曲线（含 Morph Target）进行独立压缩
- **数据库流式加载**：将多个动画的关键帧合并为数据库资产，支持按质量层级流式加载/卸载，实现"视效保真度"的动态切换
- **平台感知压缩**：支持逐平台配置压缩参数和关键帧剔除策略

## 使用场景

- 你的项目包含大量骨骼动画且包体/内存受限 → 使用 ACL 编解码器替代默认压缩
- 你需要在运行时动态调整动画质量（如远距离角色降质） → 使用 ACLDatabase + 流式加载
- 你有数百个 Morph Target 动画曲线需要压缩 → 使用 `AnimCurveCompressionCodec_ACL`
- 你需要调试压缩问题、测试不同格式 → 使用 `ACLCustom` 编解码器手动配置格式参数
- 你需要尽可能保留原始动画精度 → 使用 `ACLSafe` 编解码器

## 蓝图用法

ACLPlugin 提供的蓝图 API 集中在 ACL 数据库的视觉保真度控制上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Database Visual Fidelity` | 异步设置数据库的视觉保真度等级（Highest/Medium/Lowest），会触发流式加载 | `UAnimationCompressionLibraryDatabase` |
| `Get Database Visual Fidelity` | 获取数据库当前的视觉保真度等级 | `UAnimationCompressionLibraryDatabase` |

### 枚举类型

| 枚举 | 说明 |
|---|---|
| `ACLVisualFidelity` | 视觉保真度等级：`Highest`（最高质量，全部加载）、`Medium`（中等）、`Lowest`（最低，仅加载最高重要性层） |
| `ACLVisualFidelityChangeResult` | 切换结果：`Dispatched`（已派发）、`Completed`（完成）、`Failed`（失败） |

### 使用示例（蓝图描述）

**动态降低动画质量（蓝图）**：

1. 获取一个 `UAnimationCompressionLibraryDatabase` 资产引用
2. 使用 `Set Database Visual Fidelity` 节点（Latent），传入数据库资产和目标保真度（如 `Lowest`）
3. 节点的 `Result` 引脚使用 `ExpandEnumAsExecs`，可直接分支处理 `Dispatched` / `Completed` / `Failed`
4. 在 `Completed` 分支中执行后续逻辑

**查询当前保真度（蓝图）**：

1. 使用 `Get Database Visual Fidelity` 节点，传入数据库资产
2. 返回 `ACLVisualFidelity` 枚举值

## C++ 用法

### 头文件引入

```cpp
// 核心实现（压缩工具函数）
#include "ACLImpl.h"

// 编解码器
#include "AnimBoneCompressionCodec_ACL.h"
#include "AnimBoneCompressionCodec_ACLSafe.h"
#include "AnimBoneCompressionCodec_ACLCustom.h"
#include "AnimBoneCompressionCodec_ACLDatabase.h"
#include "AnimCurveCompressionCodec_ACL.h"

// 数据库资产
#include "AnimationCompressionLibraryDatabase.h"
```

### 基本用法：获取当前视觉保真度

```cpp
#include "AnimationCompressionLibraryDatabase.h"

// 假设 DatabaseAsset 是一个有效的 UAnimationCompressionLibraryDatabase*
UAnimationCompressionLibraryDatabase* DatabaseAsset = /* ... */;

ACLVisualFidelity CurrentFidelity = DatabaseAsset->GetVisualFidelity();
if (CurrentFidelity == ACLVisualFidelity::Lowest)
{
    // 当前是最低质量，可以考虑升级
}
```

### 进阶用法：异步切换视觉保真度（C++ Latent Action）

```cpp
#include "AnimationCompressionLibraryDatabase.h"

void AMyActor::UpgradeAnimationQuality()
{
    UAnimationCompressionLibraryDatabase* Database = LoadObject<UAnimationCompressionLibraryDatabase>(
        nullptr, TEXT("/Game/Animations/ACLDatabase.ACLDatabase"));
    
    if (!Database) return;

    // 静态蓝图接口也可以在 C++ 中调用
    FLatentActionInfo LatentInfo;
    LatentInfo.CallbackTarget = this;
    LatentInfo.ExecutionFunction = "OnFidelityChanged";
    LatentInfo.Linkage = 0;
    LatentInfo.UUID = 1;

    ACLVisualFidelityChangeResult Result;
    UAnimationCompressionLibraryDatabase::SetVisualFidelity(
        GetWorld(), LatentInfo, Database, Result, ACLVisualFidelity::Highest);
}

UFUNCTION()
void AMyActor::OnFidelityChanged()
{
    UE_LOG(LogTemp, Log, TEXT("ACL fidelity change completed!"));
}
```

### 进阶用法：使用压缩工具函数（编辑器/Commandlet 场景）

```cpp
// 来源: Public/ACLImpl.h
#if WITH_EDITORONLY_DATA

// 从 UE 的 FCompressibleAnimData 构建 ACL 轨道数组
acl::track_array_qvvf Tracks = BuildACLTransformTrackArray(
    AllocatorImpl,
    CompressibleAnimData,
    DefaultVirtualVertexDistance,   // 3.0 cm 通常合适
    SafeVirtualVertexDistance,      // 需要高精度的骨骼
    bBuildAdditiveBase,            // 是否构建 Additive 基准
    ACLPhantomTrackMode::Strip     // 剔除幽灵轨道
);

// 获取平台相关的压缩级别
acl::compression_level8 Level = GetCompressionLevel(ACLCompressionLevel::ACLCL_Medium);

#endif
```

## Demo 示例

以下示例展示如何在运行时动态切换 ACL 数据库的视觉保真度：

```cpp
// ACLFidelityController.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AnimationCompressionLibraryDatabase.h"
#include "ACLFidelityController.generated.h"

UCLASS()
class MYPROJECT_API AACLFidelityController : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "ACL")
    TObjectPtr<UAnimationCompressionLibraryDatabase> DatabaseAsset;

    UPROPERTY(EditAnywhere, Category = "ACL")
    ACLVisualFidelity TargetFidelity = ACLVisualFidelity::Highest;

    UFUNCTION(BlueprintCallable, Category = "ACL")
    void SwitchFidelity();

    UFUNCTION()
    void OnFidelitySwitched();
};
```

```cpp
// ACLFidelityController.cpp
#include "ACLFidelityController.h"

void AACLFidelityController::SwitchFidelity()
{
    if (!DatabaseAsset) return;

    FLatentActionInfo LatentInfo;
    LatentInfo.CallbackTarget = this;
    LatentInfo.ExecutionFunction = "OnFidelitySwitched";
    LatentInfo.Linkage = 0;
    LatentInfo.UUID = 100;

    ACLVisualFidelityChangeResult Result;
    UAnimationCompressionLibraryDatabase::SetVisualFidelity(
        GetWorld(), LatentInfo, DatabaseAsset, Result, TargetFidelity);
}

void AACLFidelityController::OnFidelitySwitched()
{
    ACLVisualFidelity Current = DatabaseAsset ? DatabaseAsset->GetVisualFidelity() : ACLVisualFidelity::Lowest;
    UE_LOG(LogTemp, Log, TEXT("ACL fidelity switched to: %d"), static_cast<int32>(Current));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ACLPlugin` | ACL 压缩/解压核心运行时（ACLPluginEditor 依赖它） |
| `AnimationDataController` | 动画数据编辑操作（仅 ACLPluginEditor 使用） |
| `TraceLog` | ACL 数据库流式加载的 IO 追踪日志 |
| `DesktopPlatform` | 平台相关文件操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新日志宏 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上一次错误的查找替换后重新提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退一次有问题的变更 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复委托获取方式以解决注册丢失问题 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 清理不再需要的 PVS 静态分析抑制标记 |

### 维护评价

ACLPlugin 由 Epic Games 官方维护，自 2023 年 4 月被纳入引擎目录以来持续更新。近期的提交集中在编译适配（UE_LOG 迁移、委托 API 变更）和代码清理层面，表明该插件已进入**稳定维护期**——没有大规模功能变更，但持续跟进引擎 API 变化保持兼容。

该插件默认启用（`EnabledByDefault = true`），已被 Epic 视为引擎的标准动画压缩方案之一。对于包含大量动画的项目，**强烈推荐使用**。已知限制：数据库流式加载依赖 `FByteBulkData`，仅在 Cooked 构建中生效；编辑器预览使用的是预览专用的内存流式加载器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ACLPlugin)
- [ACL 开源库](https://github.com/nicholasfrechette/acl)（上游 C++ 库）
- [官方文档](https://docs.unrealengine.com/en-US/animation-compression-library-in-unreal-engine/)（Epic 官方 ACL 文档页）