# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是 UE5 的**运行时可定制对象（Customizable Object）系统**，用于在游戏运行时根据玩家参数动态组合、修改和生成网格体、纹理和材质。

它解决的核心问题是：在角色换装、捏脸、武器皮肤等需要大量视觉变体的场景中，如果为每种组合烘焙独立资产会导致爆炸式的内存和磁盘占用。Mutable 通过一个**基于虚拟机的程序化生成管线**，在运行时根据布尔、整数、浮点、投影器等参数动态组合网格体贴图布局（Layout）、纹理层混合（Layer Blend）、网格体 Morph/Reshape/ClipDeform 等操作，按需生成最终资源。

其架构分为三层：
- **MutableTools**：编辑器编译器，将可视化节点图编译为字节码程序
- **MutableRuntime**：运行时虚拟机（`CodeRunner`），解释执行字节码生成图像、网格体、材质等资源
- **CustomizableObject**：UE 集成层，提供 `UCustomizableObject` 资产、`UCustomizableObjectInstance` 实例、`UCustomizableObjectSubsystem` 子系统等蓝图 API

## 使用场景

- 你在做一个角色换装/捏脸系统，需要运行时混合网格体、纹理和材质 → 用 Mutable
- 你需要动态生成不同外观的武器/装备，且变体数量巨大 → 用 Mutable
- 你需要运行时纹理压缩（BC/ASTC）和 Mipmap 生成 → MutableRuntime 内置 MIRO 压缩库
- 你需要将网格体变形（Morph）、Reshape、ClipDeform、Smoothing 等操作组合在一起 → Mutable 的操作图

## 模块结构总览

| 模块 | 类型 | 说明 |
|---|---|---|
| `MutableRuntime` | Runtime | 核心运行时：虚拟机、图像/网格体资源、序列化、纹理压缩 |
| `CustomizableObject` | Runtime | UE 集成层：资产、实例、子系统、蓝图 API |
| `CustomizableObjectEditor` | Runtime | 编辑器 UI：CustomizableObject 编辑器、节点图 |
| `MutableTools` | Runtime | 编译器：将节点图编译为字节码程序 |
| `MutableValidation` | Runtime | 校验器：编译期和运行时数据校验 |

## 蓝图用法

Mutable 的蓝图 API 主要通过 `UCustomizableObjectSubsystem` 和 `UCustomizableObjectInstance` 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateCustomizableObjectInstance` | 创建一个可定制对象实例 | `UCustomizableObjectSubsystem` |
| `SetIntParameterSelectedOption` | 设置整数参数选中值 | `UCustomizableObjectInstance` |
| `SetBoolParameter` | 设置布尔参数 | `UCustomizableObjectInstance` |
| `SetFloatParameter` | 设置浮点参数 | `UCustomizableObjectInstance` |
| `SetVectorParameter` | 设置颜色/向量参数 | `UCustomizableObjectInstance` |
| `SetProjectorParameter` | 设置投影器参数 | `UCustomizableObjectInstance` |
| `SetTextureParameter` | 设置纹理参数 | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsync` | 异步更新骨骼网格体 | `UCustomizableObjectInstance` |
| `GetSkeletalMesh` | 获取生成的骨骼网格体 | `UCustomizableObjectInstance` |
| `GetProjectorParameterType` | 获取投影器参数类型 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

1. **创建实例**：使用 `UCustomizableObjectSubsystem::CreateCustomizableObjectInstance` 传入一个 `UCustomizableObject` 资产引用
2. **设置参数**：依次调用 `SetIntParameterSelectedOption`（选择发型）、`SetBoolParameter`（是否戴帽子）、`SetFloatParameter`（肤色滑块）
3. **触发更新**：调用 `UpdateSkeletalMeshAsync` 异步生成结果
4. **应用结果**：在回调中调用 `GetSkeletalMesh` 获取生成的 `USkeletalMeshComponent`，设给角色 Mesh

## C++ 用法

### 头文件引入

```cpp
#include "CustomizableObjectInstance.h"
#include "CustomizableObjectSubsystem.h"
#include "MuR/External/Value.h"
```

### 基本用法

以下示例展示如何在 C++ 中创建实例并设置参数。

```cpp
// 来源: 基于 CustomizableObjectInstance API

// 获取子系统
UCustomizableObjectSubsystem* COSubsystem = UGameplayStatics::GetGameInstance(GetWorld())
    ->GetSubsystem<UCustomizableObjectSubsystem>();

// 创建实例
UCustomizableObjectInstance* Instance = COSubsystem->CreateCustomizableObjectInstance(CustomizableObject);

// 设置参数
Instance->SetIntParameterSelectedOption(TEXT("HairStyle"), TEXT("Long"));
Instance->SetBoolParameter(TEXT("HasHat"), true);
Instance->SetFloatParameter(TEXT("SkinTone"), 0.75f);

// 异步更新
Instance->UpdateSkeletalMeshAsync();
```

### 进阶用法：自定义外部资源提供器

Mutable 运行时支持通过 `FExternalResourceProvider` 接口异步加载外部纹理和网格体：

```cpp
// 来源: Internal/MuR/System.h

class FExternalResourceProvider
{
public:
    virtual ~FExternalResourceProvider() = default;

    // 异步获取外部纹理
    virtual TTuple<UE::Tasks::FTask, TFunction<void()>> GetImageAsync(
        UTexture* Texture, uint8 MipmapsToSkip, bool bLoadMipTail,
        TFunction<void(UE::Mutable::Private::TManagedPtr<FImage>)>& ResultCallback) = 0;

    // 异步获取外部网格体
    virtual TTuple<UE::Tasks::FTask, TFunction<void()>> GetMeshAsync(
        USkeletalMesh* SkeletalMesh, int32 InLODIndex, int32 InSectionIndex,
        uint8 InConversionFlags,
        TFunction<void(UE::Mutable::Private::TManagedPtr<FMesh>)>& ResultCallback) = 0;
};
```

## Demo 示例

以下是一个最小的 C++ 示例，展示如何在 GameMode 中创建并更新一个 CustomizableObject 实例。

### MyGameMode.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

class UCustomizableObject;
class UCustomizableObjectInstance;

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Mutable")
    TSoftObjectPtr<UCustomizableObject> CustomizableObjectAsset;

    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UCustomizableObjectInstance* ObjectInstance = nullptr;

    void OnUpdateCompleted();
};
```

### MyGameMode.cpp

```cpp
#include "MyGameMode.h"
#include "CustomizableObjectSubsystem.h"
#include "CustomizableObjectInstance.h"
#include "CustomizableObject.h"
#include "Kismet/GameplayStatics.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    UGameInstance* GI = UGameplayStatics::GetGameInstance(this);
    UCustomizableObjectSubsystem* Subsystem = GI->GetSubsystem<UCustomizableObjectSubsystem>();

    UCustomizableObject* CO = CustomizableObjectAsset.LoadSynchronous();
    if (!CO) return;

    ObjectInstance = Subsystem->CreateCustomizableObjectInstance(CO);
    if (!ObjectInstance) return;

    // 设置一些默认参数
    ObjectInstance->SetIntParameterSelectedOption(FName("BodyType"), 0);
    ObjectInstance->SetBoolParameter(FName("HasHelmet"), false);

    // 异步更新
    ObjectInstance->UpdateSkeletalMeshAsync(/*bNeverSkipUpdate=*/false, FOnCustomizableObjectUpdated());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MutableTools` | CustomizableObject 依赖 MutableTools 进行编译（编辑器） |
| `DerivedDataCache` | 用于缓存编译后的 Mutable 数据 |
| `MessageLog` | 编辑器日志/消息面板集成 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 关键内部架构

### MutableRuntime 核心类型

| 类 | 说明 |
|---|---|
| `FSystem` | Mutable 运行时系统入口，管理实例如 `FLiveInstance` |
| `FModel` | 编译后的可定制对象模型，包含字节码程序和常量资源 |
| `FInstance` | 一个可定制对象的运行时实例数据 |
| `FLiveInstance` | 正在处理中的实例（BeginUpdate/EndUpdate 之间） |
| `FProgram` | 字节码程序，包含操作码、状态、常量资源等 |
| `FProgramCache` | 运行时程序缓存，加速重复更新 |
| `CodeRunner` | 虚拟机执行器，解释执行字节码操作 |

### 运行时资源类型

| 类 | 说明 |
|---|---|
| `FImage` | 2D 图像资源，支持多级 Mipmap，兼容所有 EImageFormat |
| `FMesh` | 网格体资源，包含顶点缓冲、索引缓冲、骨骼映射、Morph 数据 |
| `FLayout` | 纹理布局，定义 UV 图集中的块（Block）排列 |
| `FPhysicsBody` | 物理体数据（球体、盒体、胶囊体、凸包） |
| `FSkeleton` | 骨骼数据 |

### 运行时操作（Operations）

Mutable 运行时是一个基于栈的虚拟机，`EOpType` 枚举定义了所有操作类型：

- **布尔/整数/标量/颜色/字符串**：常量、参数、条件、Switch
- **图像操作**：Layer、ColorMap、PixelFormat、Mipmap、Resize、Compose、Interpolate、Saturate、Swizzle、Displace、Transform、NormalComposite 等
- **网格体操作**：Morph、ApplyLayout、Difference、ClipDeform、ClipMorphPlane、Reshape、Smoothing、ComputeNormals、ApplyPose、Bind 等
- **材质操作**：MaterialBreak、Material 实例化

### MIRO 纹理压缩库

MutableRuntime 内置 MIRO（Mutable Internal Runtime Op），支持运行时纹理压缩：
- **BC 格式**：BC1、BC2、BC3、BC4、BC5
- **ASTC 格式**：4x4、6x6、8x8、10x10、12x12 的 RGB/RGBA/RG 变体
- 支持子图像压缩（SubImageCompression），可对图像局部区域进行压缩

### RLE 压缩

支持 RLE（Run-Length Encoding）压缩格式：
- `L_UByteRLE`：单通道 RLE
- `RGB_UByteRLE` / `RGBA_UByteRLE`：多通道 RLE
- `L_UBitRLE`：二值 RLE

### 自定义智能指针

MutableRuntime 使用自定义的 `TManagedPtr` / `TManagedRef` / `TManagedWeakPtr` 智能指针系统（`ManagedPointer.h`），其引用计数策略与引擎 `TSharedPtr` 不同：
- **弱引用也参与计数**：只有当所有强引用和弱引用都释放时才自动销毁对象
- **手动删除支持**：`TryDeleteObject()` 可在仅有唯一强引用时立即删除
- 用于管理 Mutable 内部资源的生命周期，避免循环引用问题

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名多骨骼网格体导致几何体重复的问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 蒙版裁剪操作未加载正确 Mip 级别 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复纹理参数计算 LODBias 方法错误 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 使用 ClothingAssetBase 接口支持更多服装资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能的数据竞争 |

### 维护评价

Mutable 是 **Beta 状态的活跃维护项目**。从 2024 年 9 月从 Experimental 提升到 Beta 以来，持续有功能更新和 bug 修复。最近的提交集中在修复运行时 bug（数据竞争、LOD 计算、几何重复等）和扩展功能（更多服装类型支持）。

- **创建时间**：2024 年 9 月（从 Experimental 迁移）
- **当前版本**：1.8.0
- **Beta 标记**：是（`IsBetaVersion=true`）
- **更新频率**：高频（最近几天连续有多个修复提交）
- **代码规模**：1206 个源文件，属于超大型插件
- **推荐**：适合需要运行时角色/装备自定义的项目。由于仍处于 Beta 状态，API 可能有变动，建议锁定版本使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Tests)