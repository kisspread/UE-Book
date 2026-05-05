# AxF Importer

> Importer for AxF material files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 是 |
| 模块 | AxFImporter (Editor) |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董 (>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/AxFImporter) | |

## 用途

AxF（Appearance Exchange Format）是由 X-Rite 开发的材质外观交换格式，用于精确记录物理材质的完整外观属性——包括颜色、光泽、纹理、透明度、清漆层等。该格式广泛应用于汽车、工业设计等需要高度真实材质表现的行业。

AxFImporter 插件让 Unreal Engine 5 能够直接导入 `.axf` 文件，自动将其解码并转换为 UMaterial 资产。它使用 X-Rite 提供的 AxF Decoding SDK（v1.8.1）来解析 AxF 数据，然后在 UE5 中通过材质节点图重建材质外观。

简单来说：**这个插件解决的是"如何把实物测量的材质数据原样搬进游戏引擎"的问题。**

## 使用场景

- 你从汽车制造商那里拿到了用 X-Rite 设备测量的真实车漆 `.axf` 文件 → 用 AxFImporter 导入
- 你需要在 UE5 中还原工业设计产品的精确材质外观（如金属漆、塑料、清漆涂层） → 用 AxFImporter 导入
- 你使用 VizTerra、Materialise 等工业软件导出了 AxF 格式的材质 → 用 AxFImporter 导入

## 蓝图用法

此插件是纯编辑器模块，不暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它通过 UE5 的标准文件导入机制工作，没有蓝图接口。

## C++ 用法

### 头文件引入

```cpp
#include "AxFImporterModule.h"
```

### 基本用法

该插件主要通过编辑器 UI 使用——在 Content Browser 中右键选择 Import，或直接拖放 `.axf` 文件。如果需要通过 C++ 代码触发导入，可以使用 `IAxFImporterModule` 接口：

```cpp
// 来源: Engine/Plugins/Enterprise/AxFImporter/Source/AxFImporter/Public/AxFImporterModule.h

// 检查模块是否可用
if (IAxFImporterModule::IsAvailable())
{
    IAxFImporterModule& Module = IAxFImporterModule::Get();
    
    // 检查 AxF SDK 是否成功加载
    if (Module.IsLoaded())
    {
        // 创建文件导入器实例
        IAxFFileImporter* Importer = Module.CreateFileImporter();
        
        // 设置导入选项
        UAxFImporterOptions* Options = NewObject<UAxFImporterOptions>();
        
        // 打开 AxF 文件
        Importer->OpenFile(TEXT("C:/path/to/material.axf"), *Options);
        
        // 获取文件中的材质数量
        int32 MaterialCount = Importer->GetMaterialCountInFile();
        
        // 导入材质到指定 Package
        Importer->ImportMaterials(ParentPackage, RF_Public | RF_Standalone);
        
        // 获取创建的材质
        TMap<FString, UMaterialInterface*> Materials = Importer->GetCreatedMaterials();
    }
}
```

### 进阶用法：重新导入

该插件支持 Reimport 功能。已导入的材质会在 Content Browser 右键菜单中显示 "Reimport Material" 选项。在 C++ 中：

```cpp
// 通过 FReimportManager 触发重新导入
FReimportManager::Instance()->Reimport(MaterialAsset, /*bAskForNewFileIfMissing=*/false);
```

### 导入选项

导入时会弹出选项窗口，目前只有一个配置项：

| 选项 | 说明 | 范围 |
|---|---|---|
| MetersPerSceneUnit | 材质中米与场景单位的换算比例 | 0.01 ~ 1000 |

来源：`Engine/Plugins/Enterprise/AxFImporter/Source/AxFImporter/Private/AxFImporterOptions.h`

### 支持的材质属性

根据源码分析（`AxFImporter.cpp`），该插件能解码并创建以下材质属性：

| 属性 | 说明 |
|---|---|
| Diffuse Color | 漫反射颜色 |
| Alpha | 透明度 |
| Normal | 法线贴图 |
| Specular Color | 高光颜色 |
| Specular Lobe | 高光叶瓣形状 |
| Fresnel | 菲涅尔效果 |
| Clearcoat Color | 清漆层颜色 |
| Clearcoat IOR | 清漆层折射率 |
| Clearcoat Normal | 清漆层法线 |
| Carpaint BRDF Colors | 车漆 BRDF 颜色 |
| Carpaint BTF Flakes | 车漆闪光片 |
| Height | 高度贴图 |

来源：`Engine/Plugins/Enterprise/AxFImporter/Source/AxFImporter/Private/AxFImporter.cpp`

## Demo 示例

此插件不提供独立的 Demo 项目。使用方式如下：

1. 在 Editor > Plugins 中启用 AxF Importer（默认禁用）
2. 在 Content Browser 中右键 → Import
3. 选择 `.axf` 文件
4. 在弹出的 AxF Import Options 窗口中确认导入设置
5. 导入后会在 Content Browser 中生成 `UMaterial` 资产和相关纹理

## 模块依赖

从 `AxFImporter.Build.cs` 提取的私有依赖：

| 模块 | 用途 |
|---|---|
| `Analytics` | 导入分析数据上报 |
| `Core` | 核心基础库 |
| `RenderCore` | 渲染核心 |
| `ImageCore` | 图像处理 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `MessageLog` | 消息日志窗口 |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | 编辑器功能 |
| `Slate` / `SlateCore` | UI 框架（导入选项窗口） |
| `MainFrame` | 主窗口访问 |
| `InputCore` | 输入系统 |
| `MaterialEditor` | 材质编辑器 |
| `Projects` | 插件管理 |

**第三方依赖**：AxF Decoding SDK 1.8.1（X-Rite 提供，位于 `Restricted/NotForLicensees/Source/ThirdParty/Enterprise`）。普通 UE5 源码分发不包含此 SDK，因此插件在没有 SDK 的环境下虽然编译通过但无法实际导入文件。

**公开依赖**：无。此插件不暴露公共 API 给其他模块使用。

## 维护状态

### 近期更新

| 日期 | Commit | 内容 | 解读 |
|---|---|---|---|
| 2025-06-10 | `9356818` | Disable AxF importer for Windows Arm64 | 在 `.uplugin` 中添加 `PlatformArchitectureDenyList` 排除 ARM64 平台，因为 AxF SDK DLL 仅提供 x64 版本 |
| 2023-05-12 | `31a3b39` | Remove redundant data from telemetry | 清理分析上报中的冗余数据 |
| 2022-12-12 | `e886ebc` | Adding includes that code depended on implicitly | 修复头文件隐式依赖，为后续头文件重构做准备 |

### 维护评价

- **创建时间**：2019 年 10 月，已超过 5 年
- **维护状态**：🔴 **维护不活跃**
  - 最近一次功能性更新（排除 ARM64）是 2025 年 6 月，但本质上是平台兼容性修复而非功能增强
  - 最后一次实质性功能更新时间不详，近 3 次 commit 均为基础设施维护
  - 标记为 `IsBetaVersion: true`，至今仍为 Beta 状态
  - `EnabledByDefault: false`，需要手动启用
- **平台限制**：仅支持 Win64 x64，不支持 ARM64、Linux、Mac
- **SDK 限制**：依赖 `Restricted/NotForLicensees` 中的第三方 SDK，普通源码分发无法使用
- **建议**：如果你有 `.axf` 文件需要导入，这是唯一的选择。但由于长期处于 Beta 状态且维护稀疏，建议关注是否有替代方案出现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/AxFImporter)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
