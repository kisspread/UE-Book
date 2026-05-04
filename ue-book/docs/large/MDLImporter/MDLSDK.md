# MDL SDK 集成层

> MDL SDK 与 UE5 之间的适配层，封装 NVIDIA neuray API。

## 概述

`mdl/` 子目录包含 NVIDIA MDL SDK 的 UE5 适配代码。它将 MDL SDK 的 C++ API（`mi::neuraylib::*`）封装为 UE5 风格的接口，提供材质加载、编译、蒸馏和遍历功能。

**核心类层次：**

```
IApiContext (纯虚接口)
  └── FApiContext (USE_MDLSDK 实现)
        ├── INeuray         ← MDL SDK 运行时
        ├── IMdl_compiler   ← MDL 编译器
        ├── IDatabase       ← MDL 材质数据库
        ├── IMdl_factory    ← 材质工厂
        └── FMaterialDistiller ← 材质蒸馏器

IMaterialDistiller (纯虚接口)
  └── FMaterialDistiller (USE_MDLSDK 实现)
        ├── SetBakingSettings()    ← 烘焙分辨率/采样
        ├── SetMetersPerSceneUnit() ← 单位换算
        └── Distil()               ← 执行蒸馏

IMaterialTraverser (遍历基类)
  ├── FMaterialPrinter  ← 材质打印/调试
  └── FSemanticParser   ← 语义解析

FMaterialCollection ← 材质集合容器
FMaterial           ← 单个材质的数据结构
FBakeParam          ← 烘焙参数
```

## 核心类详解

### FApiContext — MDL SDK 运行时上下文

**文件:** `mdl/ApiContext.h`, `mdl/ApiContext.cpp`

`FApiContext` 是整个 MDL SDK 集成的入口点，封装了 NVIDIA neuray 运行时的生命周期管理。

```cpp
// 创建并初始化 MDL 上下文
Mdl::FApiContext Context;

// Load() 加载 MDL SDK 动态库（libmdl_sdk.dll 等），初始化 neuray 运行时
// LibrariesPath: 包含 MDL SDK 二进制的目录
// ModulesPath: MDL 标准库搜索路径（如 C:/ProgramData/NVIDIA Corporation/mdl/）
bool bLoaded = Context.Load(LibrariesPath, ModulesPath);

// 添加自定义搜索路径
Context.AddSearchPath(TEXT("C:/MyMDLMaterials/"));
Context.AddResourceSearchPath(TEXT("C:/MyTextures/"));

// 加载 MDL 模块并提取材质
Mdl::FMaterialCollection Materials;
Context.LoadModule(TEXT("::my_module"), Materials);

// 获取蒸馏器，配置烘焙参数
Mdl::FMaterialDistiller* Distiller = Context.GetDistiller();
Distiller->SetBakingSettings(1024, 2);  // 分辨率 1024, 2x MSAA
Distiller->SetMetersPerSceneUnit(0.01f);
Distiller->Distil(Materials, ProgressCallback);

// 清理
Context.UnloadModule(TEXT("::my_module"));
Context.Unload(true);  // true = 仅清除数据库，不卸载 neuray
```

**内部 neuray 句柄：**

| 句柄 | 类型 | 用途 |
|---|---|---|
| `NeurayHandle` | `INeuray` | MDL SDK 运行时主接口 |
| `ConfigHandle` | `IMdl_configuration` | MDL 配置（搜索路径等） |
| `CompilerHandle` | `IMdl_compiler` | MDL 模块编译器 |
| `DatabaseHandle` | `IDatabase` | 材质数据库 |
| `FactoryHandle` | `IMdl_factory` | 材质实例工厂 |
| `DistillerPtr` | `FMaterialDistiller` | 材质蒸馏器 |

**条件编译：** 所有 MDL SDK 交互代码都在 `#ifdef USE_MDLSDK` 保护下。未定义该宏时，`FApiContext` 退化为空实现（所有方法返回 `false`/空值）。

### FMaterialDistiller — 材质蒸馏器

**文件:** `mdl/MaterialDistiller.h`, `mdl/MaterialDistiller.cpp`

将 MDL 材质"蒸馏"（distill）为 UE5 PBR 参数。这是 MDL→UE5 转换的核心。

```cpp
// 蒸馏器使用 MDL Distiller API 将通用 MDL BSDF 转换为目标模型参数
// 目标模型: Unreal（BaseColor, Metallic, Roughness, Normal, Emissive 等）

// 配置烘焙参数
Distiller->SetBakingSettings(Resolution, Samples);
// Resolution: 烘焙纹理分辨率（向上取整到最近的 2 的幂，最大 16384）
// Samples: MSAA 采样数（向上取整到最近的 2 的幂，最大 16）

Distiller->SetMetersPerSceneUnit(0.16f);
// 用于将 MDL 的世界空间单位转换为场景单位

// 执行蒸馏
Distiller->Distil(Materials, ProgressFunc);
// 遍历 Materials 中的每个 FMaterial
// 对每个材质：
//   1. 编译 MDL 材质实例
//   2. 使用 Distiller API 蒸馏为 Unreal 目标模型
//   3. 烘焙程序化纹理为位图（如果 MapHandler 未处理）
//   4. 填充 FMaterial 的属性（BaseColor、Metallic、Roughness 等）
```

**蒸馏流程：**

```
MDL 材质定义
    ↓
IMaterial_definition::create_function_call() → IMaterial_instance
    ↓
IMdl_factory::create_compiled_material() → ICompiled_material
    ↓
IMdl_distiller_api::distill() → 蒸馏后的 ICompiled_material
    ↓
遍历蒸馏结果，对每个属性：
  ├── 常量值 → 直接写入 FMaterial.Value
  └── 程序化表达式 → 使用 IBaker 烘焙为纹理
        ↓
填充 FMaterial 的 BaseColor/Metallic/Roughness/Normal 等
```

### FMaterial — 材质数据结构

**文件:** `mdl/Material.h`

`FMaterial` 是 MDL 材质在 UE5 侧的中间表示，包含所有 PBR 属性：

```cpp
struct Mdl::FMaterial
{
    uint32  Id;
    FString Name;      // 材质显示名
    FString BaseName;  // MDL 数据库中的基础名

    int PreferredWidth, PreferredHeight;  // 推荐烘焙尺寸

    // PBR 属性（每个属性可包含值或纹理）
    TMapEntry<FVector3f>    BaseColor;     // 基础颜色
    TMapEntry<float, 0>    Metallic;      // 金属度
    TMapEntry<float>       Specular;      // 高光
    TMapEntry<float>       Roughness;     // 粗糙度
    TMapEntry<float>       Opacity;       // 不透明度
    TMapEntry<FVector3f, 0> Emission;     // 自发光
    TPropertyEntry<float>  EmissionStrength;
    FNormalMapEntry        Normal;        // 法线贴图
    FDisplacementMapEntry  Displacement;  // 位移贴图

    // 高级材质属性
    FClearcoatEntry        Clearcoat;     // 清漆层
    FCarpaintEntry         Carpaint;      // 汽车漆面
    TPropertyEntry<FVector3f>     IOR;    // 折射率
    TPropertyEntry<FVector3f, 0>  Absorption; // 吸收系数
    TMapEntry<FVector3f, 0>       Scattering; // 散射系数

    float TilingFactor;
    FVector2D Tiling;

    // 回调函数
    FInstantiateFunc InstantiateFunction;
    FPreProcessFunc  PreProcessFunction;
    FPostProcessFunc PostProcessFunction;
};
```

**属性条目类型：**

| 类型 | 说明 |
|---|---|
| `TPropertyEntry<T>` | 纯值属性：包含 `Value` 和可选的 `ExpressionData` |
| `TMapEntry<T>` | 贴图属性：包含 `Value`、`ExpressionData` 和 `Texture`（纹理路径/源） |
| `FNormalMapEntry` | 法线贴图：包含 `ExpressionData`、`Texture` 和 `Strength` |
| `FClearcoatEntry` | 清漆：Weight + Roughness + Normal |
| `FCarpaintEntry` | 车漆：Flakes纹理数组 + ThetaFiLUT + 颜色参数 |

### FMaterialCollection — 材质集合

**文件:** `mdl/MaterialCollection.h`

简单的 `FMaterial` 数组包装，支持范围 for 循环：

```cpp
Mdl::FMaterialCollection Materials;
Materials.Reserve(10);

Mdl::FMaterial& Mat = Materials.Create();
Mat.Name = TEXT("MyMaterial");

for (Mdl::FMaterial& M : Materials)
{
    UE_LOG(LogTemp, Log, TEXT("Material: %s"), *M.Name);
}
```

### IMaterialTraverser — 编译材质遍历器

**文件:** `mdl/MaterialTraverser.h`, `mdl/MaterialTraverser.cpp`

递归遍历 MDL 编译材质的表达式树。遍历阶段：

| 阶段 | 说明 |
|---|---|
| `Parameters` | 遍历材质参数 |
| `Temporaries` | 遍历临时变量 |
| `Body` | 遍历材质主体表达式 |

**子类：**

- `FMaterialPrinter`：将材质表达式树转为可读的 MDL 代码字符串（用于调试）
- `FSemanticParser`：解析材质表达式的语义（用于判断材质类型）

### FBakeParam — 烘焙参数

**文件:** `mdl/BakeParam.h`, `mdl/BakeParam.cpp`

描述如何将 MDL 程序化表达式烘焙为纹理。

### IMapDistilHandler — 蒸馏映射处理器

**文件:** `mdl/MapDistilHandler.h`

蒸馏过程中的回调接口，允许在蒸馏时将 MDL 表达式直接转换为 UE5 材质表达式节点（而非烘焙为纹理）：

```cpp
class IMapDistilHandler
{
    virtual void PreImport(const IMaterial_definition&, const ICompiled_material&, ITransaction&) = 0;
    virtual bool Import(const FString& MapName, bool bIsTexture, FBakeParam& MapBakeParam) = 0;
    virtual void PostImport() = 0;
};
```

实现类 `FMDLMapHandler`（见 [ImportPipeline.md](ImportPipeline.md)）会在蒸馏时尝试将 MDL 表达式转为 UE5 材质节点图，仅在无法转换时才烘焙为纹理。

## MDL 路径配置

MDL SDK 通过以下路径查找模块和资源：

| 路径 | 环境变量 | Windows 默认 | 说明 |
|---|---|---|---|
| System Path | `MDL_SYSTEM_PATH` | `C:/ProgramData/NVIDIA Corporation/mdl/` | MDL 标准库 |
| User Path | `MDL_USER_PATH` | `%USERPROFILE%/mdl/` | 用户自定义模块 |

```cpp
// 获取路径（Source/MDLImporter/Private/MDLImporterOptions.cpp）
FString SysPath = UMDLImporterOptions::GetMdlSystemPath();
FString UsrPath = UMDLImporterOptions::GetMdlUserPath();
```

## 平台支持

| 平台 | SDK 二进制 | 说明 |
|---|---|---|
| Win64 | `libmdl_sdk.dll`, `mdl_distiller.dll`, `dds.dll`, `nv_freeimage.dll` | 完整支持 |
| Mac | `libmdl_sdk.so`, `mdl_distiller.so`, `dds.so`, `nv_freeimage.so` | 完整支持 |
| Linux | `libmdl_sdk.so`, `mdl_distiller.so`, `dds.so`, `nv_freeimage.so` | 完整支持 |

二进制位于 `Binaries/ThirdParty/MDL/{Platform}/` 目录。
