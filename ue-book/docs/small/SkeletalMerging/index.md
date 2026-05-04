# Skeletal Merging

> Provides Blueprint functionality to perform runtime Skeletal Mesh merging

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | SkeletalMerging (Runtime) |
| 创建时间 | 2022-01-06 |
| 年龄标签 | 🆕 (约 4.3 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SkeletalMerging) | |

## 用途

SkeletalMerging 是一个轻量级工具插件，提供在**运行时**将多个 Skeletal Mesh 或 Skeleton 合并为单一资产的蓝图函数。

它解决的核心问题是：当你在游戏运行时动态组装角色部件（如换装系统）时，需要将多个独立的骨骼网格体合并成一个完整的网格体，或者将来自不同来源的骨骼层次结构合并为一个统一的 Skeleton。

该插件本质上是对引擎内部 `FSkeletalMeshMerge` 类的一个蓝图友好封装，同时增加了独立的 Skeleton 合并功能（包括 Socket、Virtual Bone、动画曲线、Blend Profile、动画 Slot Group 等子数据的合并）。

## 使用场景

- **模块化角色换装系统**：你有一个角色由多个独立的 Skeletal Mesh 部件组成（头部、躯干、手臂、腿部），运行时需要合并为一个 Mesh 以减少 Draw Call
- **动态加载角色部件**：不同的角色装备来自不同的数据包，运行时需要合并成完整的角色 Mesh
- **跨资产 Skeleton 统一**：你从多个不同来源获取了 Skeleton，需要合并成一个统一的 Skeleton 资产以共享动画
- **LOD 优化合并**：需要在运行时将低 LOD 层级的多个 Mesh 合并为一个，用于远处角色的简化渲染

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Merge Meshes` | 将多个 Skeletal Mesh 合并为一个 | `USkeletalMergingLibrary` |
| `Merge Skeletons` | 将多个 Skeleton 合并为一个 | `USkeletalMergingLibrary` |

### FSkeletalMeshMergeParams（网格体合并参数）

| 属性 | 类型 | 说明 |
|---|---|---|
| `MeshesToMerge` | `TArray<USkeletalMesh*>` | 要合并的骨骼网格体列表 |
| `MeshSectionMappings` | `TArray<FSkelMeshMergeSectionMapping>` | 可选，将源 Mesh 的 Section 映射到合并后的 Section |
| `UVTransformsPerMesh` | `TArray<FSkelMeshMergeMeshUVTransforms>` | 可选，对每个 Mesh 的 UV 进行变换 |
| `StripTopLODS` | `int32` | 从输入 Mesh 中剥离高 LOD 层级的数量（默认 0） |
| `bNeedsCpuAccess` | `bool` | 结果 Mesh 是否需要 CPU 访问（如用于粒子生成） |
| `bSkeletonBefore` | `bool` | 是否在合并前更新 Skeleton（需同时设置 Skeleton） |
| `Skeleton` | `USkeleton*` | 指定合并后使用的 Skeleton（留空则自动生成） |

### FSkeletonMergeParams（骨骼合并参数）

| 属性 | 类型 | 说明 |
|---|---|---|
| `SkeletonsToMerge` | `TArray<USkeleton*>` | 要合并的 Skeleton 列表 |
| `bMergeSockets` | `bool` | 是否合并 Socket（默认 true） |
| `bMergeVirtualBones` | `bool` | 是否合并 Virtual Bone（默认 true） |
| `bMergeCurveNames` | `bool` | 是否合并动画曲线名称（默认 true） |
| `bMergeBlendProfiles` | `bool` | 是否合并 Blend Profile（默认 true） |
| `bMergeAnimSlotGroups` | `bool` | 是否合并动画 Slot Group（默认 true） |
| `bCheckSkeletonsCompatibility` | `bool` | 是否检查骨骼层次兼容性（默认 false） |

### 使用示例（蓝图描述）

**合并网格体**：

1. 创建一个 `FSkeletalMeshMergeParams` 变量
2. 将你要合并的多个 Skeletal Mesh 引用填入 `MeshesToMerge` 数组
3. 连接到 `Merge Meshes` 节点
4. 输出的 `USkeletalMesh*` 即为合并后的结果，可赋值给 SkeletalMeshComponent

**合并骨骼**：

1. 创建一个 `FSkeletonMergeParams` 变量
2. 将要合并的 Skeleton 引用填入 `SkeletonsToMerge` 数组
3. 根据需要调整 `bMergeSockets`、`bMergeVirtualBones` 等开关
4. 连接到 `Merge Skeletons` 节点
5. 输出的 `USkeleton*` 即为合并后的结果

## C++ 用法

### 头文件引入

```cpp
#include "SkeletalMergingLibrary.h"
```

### 基本用法 — 合并网格体

```cpp
#include "SkeletalMergingLibrary.h"

// 准备合并参数
FSkeletalMeshMergeParams MergeParams;
MergeParams.MeshesToMerge.Add(MeshA);   // USkeletalMesh*
MergeParams.MeshesToMerge.Add(MeshB);
MergeParams.MeshesToMerge.Add(MeshC);
MergeParams.StripTopLODS = 0;           // 不剥离 LOD
MergeParams.bNeedsCpuAccess = false;

// 执行合并
USkeletalMesh* MergedMesh = USkeletalMergingLibrary::MergeMeshes(MergeParams);

if (MergedMesh)
{
    // 将合并后的 Mesh 赋值给组件
    SkeletalMeshComponent->SetSkeletalMesh(MergedMesh);
}
```

*来源：`SkeletalMergingLibrary.cpp` 第 387–482 行*

### 基本用法 — 合并骨骼

```cpp
#include "SkeletalMergingLibrary.h"

// 准备合并参数
FSkeletonMergeParams SkeletonParams;
SkeletonParams.SkeletonsToMerge.Add(SkeletonA);  // USkeleton*
SkeletonParams.SkeletonsToMerge.Add(SkeletonB);
SkeletonParams.bMergeSockets = true;
SkeletonParams.bMergeVirtualBones = true;
SkeletonParams.bMergeCurveNames = true;
SkeletonParams.bCheckSkeletonsCompatibility = true; // 启用兼容性检查

// 执行合并
USkeleton* MergedSkeleton = USkeletalMergingLibrary::MergeSkeletons(SkeletonParams);

if (MergedSkeleton)
{
    // 使用合并后的 Skeleton
    SkeletalMesh->SetSkeleton(MergedSkeleton);
}
```

*来源：`SkeletalMergingLibrary.cpp` 第 90–298 行*

### 进阶用法 — 自定义 Section 映射和 UV 变换

```cpp
FSkeletalMeshMergeParams MergeParams;
MergeParams.MeshesToMerge.Add(BodyMesh);
MergeParams.MeshesToMerge.Add(ArmorMesh);

// 自定义 Section 映射：将源 Mesh 的 Section 合并到指定的目标 Section
FSkelMeshMergeSectionMapping BodyMapping;
BodyMapping.SectionIDs = {0, 1};  // 将 BodyMesh 的 Section 映射到合并后的 Section 0 和 1
FSkelMeshMergeSectionMapping ArmorMapping;
ArmorMapping.SectionIDs = {2};    // 将 ArmorMesh 的 Section 映射到合并后的 Section 2
MergeParams.MeshSectionMappings = {BodyMapping, ArmorMapping};

// UV 变换：对每个 Mesh 的 UV 通道进行缩放/偏移
FSkelMeshMergeMeshUVTransforms BodyUVTransforms;
BodyUVTransforms.UVTransforms.Add(FTransform(FRotator(0, 0, 0), FVector(0, 0, 0), FVector(1, 1, 1)));
FSkelMeshMergeMeshUVTransforms ArmorUVTransforms;
ArmorUVTransforms.UVTransforms.Add(FTransform(FRotator(0, 0, 0), FVector(0.5, 0, 0), FVector(0.5, 0.5, 1)));
MergeParams.UVTransformsPerMesh = {BodyUVTransforms, ArmorUVTransforms};

// 指定 Skeleton
MergeParams.Skeleton = MySkeleton;
MergeParams.bSkeletonBefore = true;

USkeletalMesh* MergedMesh = USkeletalMergingLibrary::MergeMeshes(MergeParams);
```

### 进阶用法 — 带兼容性检查的 Skeleton 合并

```cpp
FSkeletonMergeParams Params;
Params.SkeletonsToMerge = {CharacterSkeleton, WeaponSkeleton};
Params.bMergeSockets = true;
Params.bMergeVirtualBones = true;
Params.bMergeCurveNames = true;
Params.bMergeBlendProfiles = true;
Params.bMergeAnimSlotGroups = true;
Params.bCheckSkeletonsCompatibility = true;  // 会检查骨骼链是否冲突

USkeleton* Merged = USkeletalMergingLibrary::MergeSkeletons(Params);

if (!Merged)
{
    // 合并失败：Skeleton 之间存在不兼容的骨骼层次
    UE_LOG(LogTemp, Error, TEXT("Skeleton merge failed - incompatible bone hierarchies"));
}
```

## Demo 示例

### Build.cs 依赖

```csharp
public class MyGame : ModuleRules
{
    public MyGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "SkeletalMerging"  // 依赖 SkeletalMerging 模块
        });
    }
}
```

### 运行时换装合并示例

```cpp
// RuntimeMeshMerger.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RuntimeMeshMerger.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class URuntimeMeshMerger : public UActorComponent
{
    GENERATED_BODY()

public:
    // 要合并的 Mesh 列表（可在编辑器中设置）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mesh Merge")
    TArray<TObjectPtr<USkeletalMesh>> MeshParts;

    // 合并后的结果
    UPROPERTY(BlueprintReadOnly, Category = "Mesh Merge")
    TObjectPtr<USkeletalMesh> MergedMesh;

    // 执行合并
    UFUNCTION(BlueprintCallable, Category = "Mesh Merge")
    bool PerformMerge();

    // 合并并应用到自身的 SkeletalMeshComponent
    UFUNCTION(BlueprintCallable, Category = "Mesh Merge")
    bool MergeAndApply();
};
```

```cpp
// RuntimeMeshMerger.cpp
#include "RuntimeMeshMerger.h"
#include "SkeletalMergingLibrary.h"
#include "Components/SkeletalMeshComponent.h"

bool URuntimeMeshMerger::PerformMerge()
{
    // 过滤掉空引用
    TArray<TObjectPtr<USkeletalMesh>> ValidMeshes;
    for (const TObjectPtr<USkeletalMesh>& Mesh : MeshParts)
    {
        if (Mesh != nullptr)
        {
            ValidMeshes.Add(Mesh);
        }
    }

    if (ValidMeshes.Num() < 2)
    {
        UE_LOG(LogTemp, Warning, TEXT("至少需要 2 个有效 Mesh 才能合并"));
        return false;
    }

    FSkeletalMeshMergeParams Params;
    Params.MeshesToMerge = ValidMeshes;
    Params.StripTopLODS = 0;
    Params.bNeedsCpuAccess = false;

    MergedMesh = USkeletalMergingLibrary::MergeMeshes(Params);
    return MergedMesh != nullptr;
}

bool URuntimeMeshMerger::MergeAndApply()
{
    if (!PerformMerge())
    {
        return false;
    }

    // 获取所有者 Actor 的 SkeletalMeshComponent 并应用合并结果
    AActor* Owner = GetOwner();
    if (USkeletalMeshComponent* SKComp = Owner->FindComponentByClass<USkeletalMeshComponent>())
    {
        SKComp->SetSkeletalMesh(MergedMesh);
        return true;
    }

    return false;
}
```

## 模块依赖

该插件的 Build.cs 中所有依赖均为 `PrivateDependencyModuleNames`，但使用者需要在自己的模块中依赖 `SkeletalMerging` 本身以及以下基础模块：

| 模块 | 用途 |
|---|---|
| `SkeletalMerging` | 插件本体，提供 `USkeletalMergingLibrary` 蓝图函数库 |
| `Engine` | 提供 `USkeletalMesh`、`USkeleton`、`FSkeletalMeshMerge` 等核心类型 |
| `Core` | 基础引擎核心（通常已有） |
| `CoreUObject` | UObject 系统（通常已有） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-04-23 | `fcd8083c` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticvar instead of on types. | 构建系统调整：将 DLL 导出声明从类型级别改为方法/静态变量级别，属于 Fortnite 构建兼容性改动，无功能变化 |
| 2024-06-26 | `a783fefad` | Add functionality to add named virtual bones to a Skeleton. Fix SkeletalMergingLibrary virtual bone merging names. | **功能修复**：修复了虚拟骨骼合并时的命名问题，并为 Skeleton 添加了命名虚拟骨骼的功能。这是该插件有实质性内容的最新功能更新 |
| 2024-05-13 | `dc23af1cb` | Allow AddCurveMetaData to skip recording new transactions. | 引擎层面的小改动，`AddCurveMetaData` 支持跳过事务记录，对插件功能无直接影响 |

### 维护评价

- **年龄**：约 4.3 年（2022-01 创建），🆕 评级
- **最后实质性功能更新**：2024-06-26（虚拟骨骼合并修复），距今约 1.9 年
- **维护频率**：低。近 2 年仅 3 次提交，其中只有 1 次是功能性改动
- **稳定性**：该插件功能简单且依赖引擎核心的 `FSkeletalMeshMerge`，代码量极小（仅 2 个源文件），不存在复杂的维护需求
- **限制**：
  - `EnabledByDefault=false`，需要在项目设置中手动启用
  - 无官方文档（DocsURL 为空）
  - 无自带测试用例
  - 合并后的 Mesh 是运行时临时对象，不会自动保存为资产
- **推荐使用**：✅ 适合在运行时需要动态合并 Skeletal Mesh 的场景。功能稳定，代码简洁。但如果需要更复杂的合并控制（如引用姿势覆盖、LOD 策略等），可能需要直接使用引擎的 `FSkeletalMeshMerge` API

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SkeletalMerging)
- 引擎底层合并类：`Engine/Source/Runtime/Engine/Public/SkeletalMeshMerge.h`
