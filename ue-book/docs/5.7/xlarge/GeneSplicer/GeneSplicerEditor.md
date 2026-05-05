# GeneSplicer Plugin v9.8.2

> GeneSplicer plugin for facial animation

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeneSplicerLib` (Runtime), `GeneSplicerLibTest` (Runtime), `GeneSplicerModule` (Runtime), `GeneSplicerEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer) | |

## 用途

GeneSplicer 是一个用于**面部动画基因混合**的插件。它基于"基因池"（Gene Pool）的概念，允许从多个面部特征源中提取、混合和拼接面部动画数据。

该插件的核心功能是：
- **基因池管理**：通过 `UGenePool` 资产存储面部动画的"基因"数据（面部骨骼权重、混合形状等）
- **区域关联**：通过 `URegionAffiliation` 资产定义面部不同区域与基因特征的关联关系
- **面部动画混合**：基于基因池数据，通过数学插值生成新的面部动画姿态

该插件与 **RigLogic**（MetaHuman 面部动画系统）和 **ControlRig** 深度集成，是 MetaHuman 面部动画管线的核心组件之一。它解决的问题是：如何从一组预定义的面部特征"基因"中，通过程序化混合生成无限多样的面部动画结果。

## 使用场景

- 你在使用 MetaHuman 角色，需要自定义面部动画混合逻辑 → 用 GeneSplicer
- 你需要从多个面部动画源中提取特征并混合生成新动画 → 用 GeneSplicer
- 你需要管理复杂的面部区域关联数据（如不同面部区域对应不同的基因特征）→ 用 GeneSplicer
- 你在构建程序化角色生成系统，需要面部特征的基因混合能力 → 用 GeneSplicer

## 蓝图用法

GeneSplicer 主要是一个底层运行时库，蓝图接口较少。其核心功能通过 C++ API 暴露，蓝图层面主要通过资产导入和编辑器操作使用。

### 核心资产类型

| 资产类型 | 说明 | 导入格式 |
|---|---|---|
| `GenePool` | 面部动画基因池，存储混合形状权重等数据 | `.bpcm` 文件 |
| `RegionAffiliation` | 区域关联数据，定义面部区域与基因的映射 | `.bpcm` 文件 |

### 编辑器操作

1. **导入基因池**：在 Content Browser 中右键 → Import → 选择 `.bpcm` 文件
2. **创建基因池资产**：通过 `UGenePoolAssetFactory` 在编辑器中创建新的 GenePool 资产
3. **导入区域关联**：通过 `URegionAffiliationAssetImportFactory` 导入区域关联数据

## C++ 用法

### 头文件引入

```cpp
#include "GeneSplicerModule.h"
#include "GenePool.h"
#include "RegionAffiliationReader.h"
```

### 基本用法

GeneSplicer 的核心 API 围绕基因池的读取和面部动画数据的混合：

```cpp
// 加载基因池资产
UGenePool* GenePool = LoadObject<UGenePool>(nullptr, TEXT("/Game/MyGenePool"));

// 读取区域关联数据
URegionAffiliation* RegionAffiliation = LoadObject<URegionAffiliation>(nullptr, TEXT("/Game/MyRegionAffiliation"));
```

### 进阶用法

GeneSplicer 与 RigLogic 配合使用，通过 ControlRig 驱动面部骨骼：

```cpp
// GeneSplicer 通常在 ControlRig 的 Evaluate 阶段被调用
// 通过 RigLogic 组件获取面部动画数据
// 然后使用 GeneSplicer 的混合算法生成最终的面部姿态
```

## Demo 示例

由于 GeneSplicer 主要作为底层库使用，且与 RigLogic/ControlRig 深度集成，典型的使用方式是通过编辑器导入基因池资产，然后在 ControlRig 蓝图中引用。

```cpp
// GeneSplicerDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GeneSplicerDemo.generated.h"

UCLASS()
class AGeneSplicerDemo : public AActor
{
    GENERATED_BODY()

public:
    // 引用基因池资产
    UPROPERTY(EditAnywhere, Category = "GeneSplicer")
    UGenePool* FacialGenePool;

    // 引用区域关联资产
    UPROPERTY(EditAnywhere, Category = "GeneSplicer")
    URegionAffiliation* RegionAffiliationData;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigLogic` | MetaHuman 面部动画系统，提供面部骨骼驱动基础 |
| `ControlRig` | 程序化骨骼控制框架，用于驱动面部骨骼动画 |

## 子模块文档

由于 GeneSplicer 是一个大型插件（249 个源文件），详细文档按子模块拆分：

| 子模块 | 类型 | 说明 |
|---|---|---|
| [GeneSplicerLib](GeneSplicerLib.md) | Runtime (CPlusPlus) | 核心库，包含基因池数据结构和混合算法 |
| [GeneSplicerModule](GeneSplicerModule.md) | Runtime | 运行时模块，提供 UE 集成接口 |
| [GeneSplicerEditor](GeneSplicerEditor.md) | Runtime | 编辑器模块，提供资产导入和编辑器集成 |
| GeneSplicerLibTest | Runtime | 测试模块（仅 Win64） |

## 维护状态

### 近期更新

```
- 2024-10-21 ea76c1ecb047 Move GeneSplicer into public plugins folder #rb violeta.vukobrat
```

### 维护评价

- **创建时间**：2024-10-21，非常新的插件
- **维护状态**：该插件于 2024 年 10 月从 Epic 内部仓库移至公开插件目录，目前仅有一次公开 commit
- **依赖关系**：深度依赖 RigLogic 和 ControlRig，是 MetaHuman 面部动画管线的核心组件
- **推荐程度**：✅ 推荐使用。作为 Epic 官方维护的 MetaHuman 面部动画核心组件，虽然公开 commit 较少，但这很可能是因为主要开发在 Epic 内部进行。该插件是 MetaHuman 工作流的必要组件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer)
- [RigLogic 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic)
- [ControlRig 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig)

---

# GeneSplicerEditor 子模块

> 编辑器集成模块，提供 GenePool 和 RegionAffiliation 资产的编辑器支持

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Runtime |
| 路径 | `Engine/Plugins/Animation/GeneSplicer/Source/GeneSplicerEditor/` |

## 功能概述

GeneSplicerEditor 模块提供以下编辑器集成功能：

1. **资产类型注册**：注册 GenePool 和 RegionAffiliation 资产类型，使其在 Content Browser 中可见
2. **资产工厂**：提供创建和导入 GenePool/RegionAffiliation 资产的工厂类
3. **文件导入**：支持从 `.bpcm` 文件导入基因池和区域关联数据

## 核心类

### FGeneSplicerEditorModule

编辑器模块主类，负责注册资产类型操作。

```cpp
class FGeneSplicerEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
private:
    TSharedPtr<FGenePoolAssetTypeActions> GenePoolAssetTypeActions;
};
```

### FGenePoolAssetTypeActions

GenePool 资产的编辑器操作定义。

```cpp
class FGenePoolAssetTypeActions : public FAssetTypeActions_Base
{
public:
    UClass* GetSupportedClass() const override;
    FText GetName() const override;
    FColor GetTypeColor() const override;
    uint32 GetCategories() override;
};
```

### FRegionAffiliationAssetTypeActions

RegionAffiliation 资产的编辑器操作定义。

```cpp
class FRegionAffiliationAssetTypeActions : public FAssetTypeActions_Base
{
public:
    UClass* GetSupportedClass() const override;
    FText GetName() const override;
    FColor GetTypeColor() const override;
    uint32 GetCategories() override;
};
```

### UGenePoolAssetFactory

GenePool 资产创建工厂。

```cpp
UCLASS()
class UGenePoolAssetFactory : public UFactory
{
    GENERATED_BODY()
public:
    UGenePoolAssetFactory();
    virtual UObject* FactoryCreateNew(UClass* Class, UObject* InParent, FName Name, 
                                       EObjectFlags Flags, UObject* Context, 
                                       FFeedbackContext* Warn) override;
};
```

### UGenePoolAssetImportFactory

GenePool 文件导入工厂，支持从 `.bpcm` 文件导入。

```cpp
UCLASS()
class UGenePoolAssetImportFactory : public UFactory
{
    GENERATED_BODY()
public:
    UGenePoolAssetImportFactory();
    virtual UObject* FactoryCreateFile(UClass* InClass, UObject* InParent, FName InName,
                                        EObjectFlags Flags, const FString& Filename,
                                        const TCHAR* Parms, FFeedbackContext* Warn,
                                        bool& bOutOperationCanceled) override;
    virtual bool FactoryCanImport(const FString& Filename) override;
};
```

### URegionAffiliationAssetImportFactory

RegionAffiliation 文件导入工厂。

```cpp
UCLASS()
class URegionAffiliationAssetImportFactory : public UFactory
{
    GENERATED_BODY()
public:
    URegionAffiliationAssetImportFactory();
    virtual UObject* FactoryCreateFile(UClass* InClass, UObject* InParent, FName InName,
                                        EObjectFlags Flags, const FString& Filename,
                                        const TCHAR* Parms, FFeedbackContext* Warn,
                                        bool& bOutOperationCanceled) override;
    virtual bool FactoryCanImport(const FString& Filename) override;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeneSplicerLib` | 核心库，提供 GenePool 和 RegionAffiliation 数据结构 |

---

# GeneSplicerLib 子模块

> 核心库模块，包含基因池数据结构和面部动画混合算法

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Runtime (CPlusPlus) |
| 路径 | `Engine/Plugins/Animation/GeneSplicer/Source/GeneSplicerLib/` |

## 功能概述

GeneSplicerLib 是 GeneSplicer 插件的核心库，提供：

1. **基因池数据结构**：`UGenePool` 类，存储面部动画的基因数据
2. **区域关联读取**：`URegionAffiliation` 类，管理面部区域与基因的映射关系
3. **混合算法**：基于基因池数据的面部动画混合计算
4. **文件格式支持**：`.bpcm` 文件的读写支持

## 核心类

### UGenePool

基因池资产类，存储面部动画的基因数据（混合形状权重、骨骼变换等）。

### URegionAffiliation

区域关联资产类，定义面部不同区域与基因特征的关联关系。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器基础支持（用于资产序列化） |

---

# GeneSplicerModule 子模块

> 运行时模块，提供 GeneSplicer 的 UE 集成接口

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Runtime |
| 路径 | `Engine/Plugins/Animation/GeneSplicer/Source/GeneSplicerModule/` |

## 功能概述

GeneSplicerModule 是 GeneSplicer 的运行时集成模块，负责：

1. **模块初始化**：注册 GeneSplicer 运行时服务
2. **RigLogic 集成**：与 RigLogic 面部动画系统集成
3. **ControlRig 集成**：通过 ControlRig 驱动面部骨骼

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器基础支持 |