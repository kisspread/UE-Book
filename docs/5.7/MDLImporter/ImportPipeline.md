# 导入管线

> MDL 文件的完整导入和重新导入流程。

## 概述

导入管线是 MDL Importer 插件的入口层，负责将 `.mdl` 文件导入为 UE5 材质资产。它由以下组件组成：

```
UMDLImporterFactory (UFactory + FReimportHandler)
  ├── 注册 ".mdl" 文件扩展名
  ├── FactoryCreateFile() → 显示选项窗口 → 创建 IMdlFileImporter
  └── Reimport() → 重新导入已有的材质

IMdlFileImporter (接口)
  └── FMdlFileImporterImpl (实现)
        └── 委托给 FMDLImporter

FMDLImporter (核心导入逻辑)
  ├── OpenFile() → 加载 MDL 模块
  ├── LoadModule() → 提取材质
  ├── ImportMaterials() → 创建 UMaterial + 蒸馏
  └── Reimport() → 重新导入单个材质

FMdlMaterialImporter (静态 API)
  ├── ImportMaterialFromModule() → 从模块名导入单个材质
  └── FScopedSearchPath → RAII 搜索路径管理

FMDLImporterModule (编辑器模块)
  ├── 懒加载 FMDLImporter 实例
  ├── 注册 Content Browser 右键菜单
  └── 管理模块生命周期

SMDLOptionsWindow (Slate UI)
  └── 导入选项对话框
```

## UMDLImporterFactory — 导入工厂

**文件:** `MDLImporterFactory.h`, `MDLImporterFactory.cpp`

继承自 `UFactory` 和 `FReimportHandler`，是 UE5 编辑器识别 `.mdl` 文件的入口。

### 注册信息

```cpp
// 构造函数中
bCreateNew = bText = false;
bEditorImport = true;
SupportedClass = UMaterial::StaticClass();
ImportPriority += 100;  // 高优先级，优先于其他材质导入器

Formats = {"mdl;MDL material files"};
```

### FactoryCreateFile 流程

```
1. 检查 MDL SDK 可用性
2. 创建 UMDLImporterOptions（临时对象）
3. 显示导入选项窗口（SMDLOptionsWindow）
   - 如果是 Commandlet/无人值守模式，跳过窗口
4. 广播 AssetPreImport 事件
5. 创建 IMdlFileImporter
6. 调用 LoadMaterials():
   a. Importer->OpenFile(Filename, Options)
   b. Importer->ImportMaterials(Package, Flags, ProgressFunc)
7. 获取创建的材质，处理单材质/多材质情况
8. 广播 AssetPostImport 事件
9. 发送分析遥测（ImportDuration, ImportSuccess/Fail）
10. 返回导入的 UObject
```

### Reimport 流程

```
1. 验证 Obj 是 UMaterialInterface 且来自 .mdl 文件
2. 获取原始文件路径
3. 创建新的 IMdlFileImporter
4. 调用 Importer->Reimport(FileName, Options, Material)
5. 收集日志消息，显示错误/警告
```

## FMDLImporter — 核心导入器

**文件:** `MDLImporter.h`, `MDLImporter.cpp`

封装完整的 MDL 导入逻辑，协调 ApiContext、MaterialDistiller、MaterialFactory 之间的交互。

### 构造与初始化

```cpp
FMDLImporter::FMDLImporter(const FString& PluginPath)
{
    // 1. 确定平台路径
    ThirdPartyPath = PluginPath + "/Binaries/ThirdParty/MDL/" + Platform;

    // 2. 创建 MDL API 上下文
    MdlContext.Reset(new Mdl::FApiContext());

    // 3. 加载 MDL SDK（动态库 + 标准库路径）
    if (MdlContext->Load(ThirdPartyPath, UMDLImporterOptions::GetMdlSystemPath()))
    {
        // 4. 添加用户路径
        MdlContext->AddSearchPath(MdlUserPath);
        MdlContext->AddResourceSearchPath(MdlUserPath);

        // 5. 创建蒸馏映射处理器
        DistillationMapHandler.Reset(new FMDLMapHandler(*MdlContext));
    }
}
```

### OpenFile 流程

```cpp
bool FMDLImporter::OpenFile(const FString& InFileName,
                             const UMDLImporterOptions& InImporterOptions,
                             Mdl::FMaterialCollection& OutMaterials)
{
    // 1. 设置搜索路径
    //    - 用户配置的 ModulesDir 和 ResourcesDir
    //    - 文件所在目录及其所有父目录（递归向上）

    // 2. 将文件路径转换为 MDL 模块名
    ActiveModuleName = UE::Mdl::Util::ConvertFilePathToModuleName(InFileName);
    // 例: "C:/path/to/my_material.mdl" → "::path::to::my_material"

    // 3. 加载模块
    bSuccess = LoadModule(ActiveModuleName, InImporterOptions, OutMaterials);

    // 4. 清理搜索路径

    // 5. 配置蒸馏映射处理器
    //    bForceBaking=true 时不使用 MapHandler（全部烘焙为纹理）
    MapHandler = InImporterOptions.bForceBaking ? nullptr : DistillationMapHandler.Get();
    MdlContext->GetDistiller()->SetMapHanlder(MapHandler);

    return bSuccess;
}
```

### ImportMaterials 流程

```cpp
bool FMDLImporter::ImportMaterials(UObject* ParentPackage, EObjectFlags Flags,
                                    Mdl::FMaterialCollection& Materials,
                                    FProgressFunc ProgressFunc)
{
    // 1. 创建纹理工厂
    UTextureFactory* Factory = NewObject<UTextureFactory>();
    SetTextureFactory(Factory);

    // 2. 创建材质骨架（UMaterial 对象）
    MaterialFactory->CreateMaterials(ActiveFilename, ParentPackage, Flags, Materials);

    // 3. 蒸馏材质
    //    - 设置 MapHandler 的材质映射
    //    - 调用 Distiller->Distil() 填充 FMaterial 属性
    DistillMaterials(MaterialFactory->GetNameMaterialMap(), Materials, ProgressFunc);

    // 4. 后处理（连接材质表达式、设置 Shading Model 等）
    MaterialFactory->PostImport(Materials);

    // 5. 处理虚拟纹理兼容性
    ConvertUnsuportedVirtualTextures();
}
```

### Reimport 流程

```cpp
bool FMDLImporter::Reimport(const FString& InFileName,
                             const UMDLImporterOptions& InImporterOptions,
                             UMaterialInterface* OutMaterial)
{
    // 1. 重新打开 MDL 文件
    Mdl::FMaterialCollection Materials;
    OpenFile(InFileName, InImporterOptions, Materials);

    // 2. 找到匹配的材质，禁用其他材质
    for (FMaterial& M : Materials)
    {
        if (M.Name != OutMaterial->GetName())
            M.Disable();
    }

    // 3. 清除现有材质属性
    ClearMaterial(Cast<UMaterial>(OutMaterial));

    // 4. 重新蒸馏
    DistillMaterials(MaterialsMap, Materials, nullptr);

    // 5. 重新连接材质表达式
    MaterialFactory->Reimport(MdlMaterial, *Material);
}
```

## FMdlMaterialImporter — 静态导入 API

**文件:** `MDLMaterialImporter.h`, `MDLMaterialImporter.cpp`

提供从外部模块导入 MDL 材质的简单接口：

```cpp
class FMdlMaterialImporter
{
public:
    // 从 MDL 模块名和定义名导入单个材质
    static UMaterialInterface* ImportMaterialFromModule(
        UPackage* ParentPackage,
        EObjectFlags ObjectFlags,
        const FString& MdlModuleName,      // 如 "::my_module"
        const FString& MdlDefinitionName,   // 如 "my_material"
        const UMDLImporterOptions& ImporterOptions
    );

    // 搜索路径管理
    static void AddSearchPath(const FString& SearchPath);
    static void RemoveSearchPath(const FString& SearchPath);

    // RAII 搜索路径
    struct FScopedSearchPath { ... };
};
```

### 模块名转换

```cpp
// UE::Mdl::Util::ConvertFilePathToModuleName()
// 将文件路径转换为 MDL 模块名格式
//
// 输入: "C:/path/to/my_material.mdl"
// 处理: 1. 移除扩展名 → "C:/path/to/my_material"
//       2. 移除盘符 → "/path/to/my_material"
//       3. 替换 / 为 :: → "::path::to::my_material"
//       4. 确保 :: 前缀
// 输出: "::path::to::my_material"
```

## UMDLImporterOptions — 导入选项

**文件:** `MDLImporterOptions.h`, `MDLImporterOptions.cpp`

```cpp
UCLASS(config = Engine, defaultconfig)
class UMDLImporterOptions : public UObject
{
    // 烘焙选项
    UPROPERTY(config, EditAnywhere, Category="Bake options")
    uint32 BakingResolution = 1024;    // 128-16384，2的幂

    UPROPERTY(config, EditAnywhere, Category="Bake options")
    uint32 BakingSamples = 2;          // 1-16，2的幂

    // 高级选项
    UPROPERTY(config, EditAnywhere, Category="Advanced options")
    FDirectoryPath ResourcesDir;       // 纹理/资源搜索路径

    UPROPERTY(config, EditAnywhere, Category="Advanced options")
    FDirectoryPath ModulesDir;         // MDL 模块搜索路径

    // 隐藏属性
    float MetersPerSceneUnit = 0.16f;  // 场景单位换算
    bool bForceBaking = false;         // 强制烘焙所有贴图
};
```

## SMDLOptionsWindow — 导入选项窗口

**文件:** `UI/MDLOptionsWindow.h`, `UI/MDLOptionsWindow.cpp`

Slate 窗口，在导入 `.mdl` 文件时弹出，显示：
- 文件名
- 目标包路径
- 材质数量（通过解析 `export material` 关键字计数）
- 导入选项属性编辑器

用户可以修改烘焙分辨率、搜索路径等参数后点击 Import 或 Cancel。

## FMDLImporterModule — 编辑器模块

**文件:** `MDLImporterModule.h`, `MDLImporterModule.cpp`

模块入口，处理：
- **懒加载**：`GetMDLImporter()` 首次调用时才创建 `FMDLImporter` 实例
- **Shader 映射**：映射 `/Plugin/MDLImporter` 到插件的 Shaders 目录
- **Content Browser 集成**：为 MDL 导入的材质添加"Reimport Material"右键菜单项

```cpp
// Content Browser 右键菜单
// 选中从 .mdl 导入的材质时，显示 "Reimport Material" 菜单项
// 批量支持：可同时选中多个材质进行重新导入
```

## FMDLMapHandler — 蒸馏映射处理器

**文件:** `MDLMapHandler.h`, `MDLMapHandler.cpp`

在蒸馏过程中，将 MDL 表达式直接转换为 UE5 材质表达式节点（而非烘焙为纹理）。这是性能和质量的关键优化：

```
Distiller 调用 MapHandler->Import(MapName, bIsTexture, BakeParam)
  ├── 返回 true  → 表达式已转换为 UE5 节点，跳过烘焙
  └── 返回 false → 由 Distiller 烘焙为纹理
```

MapHandler 内部使用 `FMaterialExpressionFactory` 来创建 UE5 表达式节点，并将其连接到对应的材质属性。
