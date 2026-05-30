# Dynamic Material Texture Set

> Compact dynamic material creator and editor, similar in style to other DDCs.

| 属性 | 值 |
|---|---|
| 中文名 | 动态材质纹理集 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质纹理映射数据资产） |
| 模块 | `DynamicMaterial` (RuntimeAndProgram), `DynamicMaterialTextureSet` (RuntimeAndProgram), `DynamicMaterialEditor` (Editor), `DynamicMaterialTextureSetEditor` (Editor), `DynamicMaterialShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

## 用途

DynamicMaterial 是一个用于虚幻引擎虚拟制作（Virtual Production）流程的动态材质创建和编辑插件。它提供了一种紧凑的、类似 DDC（Derived Data Cache）风格的工作流，允许用户通过纹理集（Texture Set）快速创建和管理材质参数。

**DynamicMaterialTextureSet 模块**专注于纹理集的数据结构和管理。它解决的核心问题是：将一组常用的纹理（BaseColor、Normal、Metallic、Roughness 等材质属性）打包为一个可复用的资产 `UDMTextureSet`，并支持按通道（R/G/B/A）选择纹理的特定通道作为材质输入。这在 Motion Design、虚拟制片等需要快速切换材质外观的场景中非常实用。

## 使用场景

- 你在做 Motion Design 项目，需要快速为多个物体配置 PBR 材质贴图 → 用 UDMTextureSet 将一组纹理打包为资产
- 你需要将一张纹理的特定通道（如 R 通道）映射到 Metallic 属性，G 通道映射到 Roughness → 用 EDMTextureChannelMask 进行通道选择
- 你在虚拟制片中需要动态切换材质外观（白天/夜晚纹理集）→ 运行时创建多个 UDMTextureSet 并热切换
- 你需要蓝图中查询或设置某个材质属性是否有纹理 → 用 HasMaterialProperty / HasMaterialTexture 节点

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasMaterialProperty` | 检查纹理集是否包含指定材质属性（不检查是否已分配纹理） | `UDMTextureSet` |
| `HasMaterialTexture` | 检查指定材质属性是否已分配纹理 | `UDMTextureSet` |
| `GetMaterialTexture` | 获取指定材质属性对应的纹理信息（纹理对象+通道掩码） | `UDMTextureSet` |
| `SetMaterialTexture` | 为指定材质属性设置纹理（传入空可取消分配） | `UDMTextureSet` |
| `ContainsTexture` | 检查纹理集中是否包含某个特定纹理对象 | `UDMTextureSet` |

### 使用示例

**创建纹理集并配置 PBR 贴图：**

1. 创建一个 `UDMTextureSet` 对象（New Object 或 Spawn Actor 时自动创建）
2. 构造 `FDMMaterialTexture` 结构体，设置 Texture 引用和 ChannelMask
3. 调用 `SetMaterialTexture` 为 BaseColor / Normal / Metallic / Roughness 等属性分配纹理
4. 在材质实例中读取纹理集数据，应用到对应材质参数

**查询纹理集状态：**

1. 调用 `HasMaterialProperty(MP_BaseColor)` → 检查纹理集中是否定义了 BaseColor 属性
2. 调用 `HasMaterialTexture(MP_BaseColor)` → 检查 BaseColor 是否已分配纹理
3. 调用 `GetMaterialTexture(MP_BaseColor, OutTexture)` → 获取纹理对象和通道掩码

**多通道纹理拆分：**

将一张 ORM（Occlusion/Roughness/Metallic）打包纹理拆分使用：
- AmbientOcclusion → Texture=ORM, ChannelMask=`Red`
- Roughness → Texture=ORM, ChannelMask=`Green`
- Metallic → Texture=ORM, ChannelMask=`Blue`

## C++ 用法

### 头文件引入

```cpp
#include "DMTextureSet.h"
#include "DMMaterialTexture.h"
#include "DMTextureSetMaterialProperty.h"
#include "DMTextureChannelMask.h"
```

### 基本用法

创建纹理集并管理材质属性到纹理的映射：

```cpp
// 创建纹理集
UDMTextureSet* TextureSet = NewObject<UDMTextureSet>();

// 准备纹理数据
FDMMaterialTexture MatTexture;
MatTexture.Texture = SomeBaseColorTexture;    // TSoftObjectPtr<UTexture>
MatTexture.TextureChannel = EDMTextureChannelMask::RGB;

// 设置材质属性的纹理
TextureSet->SetMaterialTexture(EDMTextureSetMaterialProperty::BaseColor, MatTexture);

// 查询
bool bHasProperty = TextureSet->HasMaterialProperty(EDMTextureSetMaterialProperty::BaseColor);
bool bHasTexture = TextureSet->HasMaterialTexture(EDMTextureSetMaterialProperty::BaseColor);

// 获取纹理信息
FDMMaterialTexture OutTexture;
if (TextureSet->GetMaterialTexture(EDMTextureSetMaterialProperty::BaseColor, OutTexture))
{
    UTexture* Tex = OutTexture.Texture.Get();
    EDMTextureChannelMask Channels = OutTexture.TextureChannel;
}
```

### 进阶用法

使用单张 ORM 纹理拆分为多个材质属性，利用通道掩码：

```cpp
// 一张 ORM 纹理包含三个通道
TSoftObjectPtr<UTexture> ORMTexture = LoadObject<UTexture>(nullptr, TEXT("/Game/Tex_ORM"));

// Ambient Occlusion = Red 通道
FDMMaterialTexture AO;
AO.Texture = ORMTexture;
AO.TextureChannel = EDMTextureChannelMask::Red;
TextureSet->SetMaterialTexture(EDMTextureSetMaterialProperty::AmbientOcclusion, AO);

// Roughness = Green 通道
FDMMaterialTexture Roughness;
Roughness.Texture = ORMTexture;
Roughness.TextureChannel = EDMTextureChannelMask::Green;
TextureSet->SetMaterialTexture(EDMTextureSetMaterialProperty::Roughness, Roughness);

// Metallic = Blue 通道
FDMMaterialTexture Metallic;
Metallic.Texture = ORMTexture;
Metallic.TextureChannel = EDMTextureChannelMask::Blue;
TextureSet->SetMaterialTexture(EDMTextureSetMaterialProperty::Metallic, Metallic);

// 检查纹理集中是否包含该 ORM 纹理
bool bFound = TextureSet->ContainsTexture(ORMTexture.Get()); // true

// 遍历所有纹理映射
const TMap<EDMTextureSetMaterialProperty, FDMMaterialTexture>& AllTextures = TextureSet->GetTextures();
for (const auto& Pair : AllTextures)
{
    EDMTextureSetMaterialProperty Prop = Pair.Key;
    const FDMMaterialTexture& Tex = Pair.Value;
    // ...
}
```

### 关键类型说明

| 类型 | 说明 |
|---|---|
| `EDMTextureSetMaterialProperty` | 材质属性枚举，值与 `EMaterialProperty` 一一对应（BaseColor、Normal、Metallic 等） |
| `EDMTextureChannelMask` | 位掩码枚举，支持 `Red`、`Green`、`Blue`、`Alpha` 及组合（`RGB`、`RGBA`） |
| `FDMMaterialTexture` | 结构体，包含 `TSoftObjectPtr<UTexture>` 纹理引用 + `EDMTextureChannelMask` 通道掩码 |

## Demo 示例

```cpp
// MyMaterialSwitcher.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DMTextureSet.h"
#include "DMMaterialTexture.h"
#include "DMTextureSetMaterialProperty.h"
#include "DMTextureChannelMask.h"
#include "MyMaterialSwitcher.generated.h"

UCLASS()
class AMyMaterialSwitcher : public AActor
{
    GENERATED_BODY()

public:
    AMyMaterialSwitcher();

    UPROPERTY(EditAnywhere, Category = "Material")
    TObjectPtr<UDMTextureSet> DayTextureSet;

    UPROPERTY(EditAnywhere, Category = "Material")
    TObjectPtr<UDMTextureSet> NightTextureSet;

    UFUNCTION(BlueprintCallable, Category = "Material")
    void SwitchToDay();

    UFUNCTION(BlueprintCallable, Category = "Material")
    void SwitchToNight();

    UFUNCTION(BlueprintCallable, Category = "Material")
    void QueryTextureSet(UDMTextureSet* InTextureSet);

private:
    UPROPERTY()
    bool bIsDay = true;
};
```

```cpp
// MyMaterialSwitcher.cpp
#include "MyMaterialSwitcher.h"
#include "Engine/Texture2D.h"

AMyMaterialSwitcher::AMyMaterialSwitcher()
{
    PrimaryActorTick.bCanEverTick = false;
    DayTextureSet = CreateDefaultSubobject<UDMTextureSet>(TEXT("DayTextureSet"));
    NightTextureSet = CreateDefaultSubobject<UDMTextureSet>(TEXT("NightTextureSet"));
}

void AMyMaterialSwitcher::SwitchToDay()
{
    // 假设 DayTextureSet 已在编辑器中配置好
    // 可在运行时动态修改
    FDMMaterialTexture EmissiveOverride;
    EmissiveOverride.Texture = nullptr;
    EmissiveOverride.TextureChannel = EDMTextureChannelMask::RGB;
    DayTextureSet->SetMaterialTexture(EDMTextureSetMaterialProperty::EmissiveColor, EmissiveOverride);
    bIsDay = true;
}

void AMyMaterialSwitcher::SwitchToNight()
{
    bIsDay = false;
}

void AMyMaterialSwitcher::QueryTextureSet(UDMTextureSet* InTextureSet)
{
    if (!InTextureSet)
    {
        return;
    }

    // 查询各属性
    TArray<EDMTextureSetMaterialProperty> Properties = {
        EDMTextureSetMaterialProperty::BaseColor,
        EDMTextureSetMaterialProperty::Normal,
        EDMTextureSetMaterialProperty::Metallic,
        EDMTextureSetMaterialProperty::Roughness,
        EDMTextureSetMaterialProperty::AmbientOcclusion,
    };

    for (EDMTextureSetMaterialProperty Prop : Properties)
    {
        if (InTextureSet->HasMaterialProperty(Prop))
        {
            FDMMaterialTexture MatTex;
            if (InTextureSet->GetMaterialTexture(Prop, MatTex))
            {
                UE_LOG(LogTemp, Log, TEXT("Property %d has texture, channel mask: %d"),
                    (uint8)Prop, (uint8)MatTex.TextureChannel);
            }
            else
            {
                UE_LOG(LogTemp, Log, TEXT("Property %d defined but no texture assigned"), (uint8)Prop);
            }
        }
    }
}
```

## 模块依赖

DynamicMaterialTextureSet 模块的 Build.cs 未提供详细依赖列表，但根据头文件分析：

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | 核心运行时模块，提供基础材质类型和通道掩码定义 |
| `CustomDetailsView` | 插件级依赖，提供自定义细节面板 UI |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | Motion Design 将关卡编辑器中的场景设置和大纲面板迁移至独立分组 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构：客户端关联/解关联时通知机制改进 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚变更 CL53913857 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口重构：客户端关联/解关联通知机制（重复提交修正版） |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |

### 维护评价

- **创建时间**：2025-05-09，非常年轻的插件
- **来源**：从 `/Plugins/Experimental` 迁移到 `/Plugins/VirtualProduction`，说明已通过内部审核，不再是实验性质
- **最近更新**：近期更新活跃（2026-05 月有多次提交），主要涉及 Motion Design 集成和视口重构，与 DynamicMaterialTextureSet 本身关系不大
- **维护状态**：活跃维护中，作为 Epic 官方维护的 Virtual Production 插件套件的一部分
- **推荐程度**：✅ 推荐使用。作为 Virtual Production 工具链的核心组件，有 Epic 官方支持，API 设计清晰，适合需要动态材质管理的项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现独立测试文件）