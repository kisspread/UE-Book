# Datasmith MVR

> Enabled support to import .udatasmith files with MVR content.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production (DMX) |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | DatasmithMVRTranslator (Editor) |
| 创建时间 | 2022-05-04 |
| 年龄标签 | 🆕 (~4年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DatasmithMVR) | |

## 用途

DatasmithMVR 是一个 Datasmith Translator 扩展插件，让 UE5 的 Datasmith 导入管线在导入 `.udatasmith` 文件时，**自动检测并处理同目录下的 MVR (My Virtual Rig) 文件**。

MVR 是灯光行业（Vectorworks 等 CAD 软件）用于描述 3D 场景中灯光 Fixture 位置、类型和 DMX 地址信息的开放文件格式。本插件的核心价值是：**在 Datasmith 导入流程中一并完成 MVR 的解析**，将 MVR 中的灯具信息转换为 UE 的 DMX Library 和 DMX MVR Scene Actor，从而实现灯光 CAD 场景到 UE5 的一步到位导入，无需手动分步操作。

简单来说：导入一个 Datasmith 场景，如果有配套的 MVR 文件，灯具信息会自动变成可接收 DMX 信号的虚拟灯光 Actor。

## 使用场景

- **演出灯光预可视化 (Previs)**：你用 Vectorworks 设计了舞台灯光布局并导出 Datasmith + MVR，想在 UE5 中一键导入整个场景（3D 几何体 + 灯具 Fixture 信息），然后通过 DMX 控制灯光进行预演。
- **虚拟制作 (Virtual Production)**：你的灯光设计师在 Vectorworks 中布置好了灯光并导出 MVR，你需要在 UE5 的 nDisplay / LED Volume 环境中使用这些灯光数据。
- **DMX 灯光模拟**：你有一个包含 DMX 灯具信息的 MVR 文件，想在 UE5 中生成对应的 DMX Fixture Patch，然后通过 sACN / Art-Net 等协议控制它们。

## 工作原理

插件的工作方式是在运行时**替换** Datasmith 的默认 Native Translator（`FDatasmithNativeTranslator`），注册自己的 `FDatasmithMVRNativeTranslator`。具体流程如下：

1. **加载场景**：先调用原生 `FDatasmithNativeTranslator::LoadScene()` 完成标准 Datasmith 场景加载
2. **检查导入选项**：读取 `UDatasmithMVRImportOptions`，如果 `bImportMVR` 为 false 则跳过 MVR 处理
3. **查找 MVR 文件**：在 `.udatasmith` 文件的同级目录或 `_Assets` 子目录中查找同名 `.mvr` 文件（兼容 Vectorworks 的下划线/空格命名差异）
4. **创建 DMX Library**：使用 `UDMXLibraryFromMVRFactory` 从 MVR 文件创建 `UDMXLibrary` 资产
5. **替换场景元素**：在 Datasmith Scene 中，将 MVR Fixture 对应的原始几何体 Actor 替换为一个 `ADMXMVRSceneActor`，并通过 Metadata 关联 DMX Library

**重要限制**：MVR 导入仅在使用传统 Datasmith 导入管线时有效，**不支持 Interchange 管线**（Interchange 在独立线程上导入，无法修改场景数据）。使用 Interchange 导入时会显示通知提示。

## 导入配置

### 导入选项 (UDatasmithMVRImportOptions)

导入 Datasmith 场景时，在导入选项对话框中会出现 MVR 相关配置：

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bImportMVR` | bool | `true` | 是否导入 MVR 内容。设为 false 时仅导入标准 Datasmith 场景，忽略 MVR |

该选项保存在每个项目的用户设置中 (`Config = EditorPerProjectUserSettings`)。

### MVR 文件查找规则

当导入 `MyScene.udatasmith` 时，插件按以下顺序查找 MVR 文件：

1. `MyScene.mvr`（同目录）
2. `MyScene_Assets/MyScene.mvr`（Assets 子目录）
3. `My Scene.mvr`（同目录，空格替代下划线——兼容 Vectorworks 默认行为）
4. `MyScene_Assets/My Scene.mvr`（Assets 子目录，空格替代下划线）

找到第一个存在的文件即使用。

## 蓝图用法

本插件不暴露 BlueprintCallable 函数。它是一个纯 Editor 模块，仅在 Datasmith 导入流程中作为 Translator 运行，没有蓝图交互接口。

导入完成后，场景中会生成一个 `ADMXMVRSceneActor`，你可以在蓝图中通过以下方式与之交互（这些功能来自 DMXEngine 插件，非本插件直接提供）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDMXLibrary` | 获取该 MVR 场景关联的 DMX Library | `ADMXMVRSceneActor` |
| `GetRelatedActors` | 获取场景中所有关联的 Fixture Actor | `ADMXMVRSceneActor` |
| `GetActorsSpawnedForFixtureType` | 获取指定 Fixture Type 生成的所有 Actor | `ADMXMVRSceneActor` |

## C++ 用法

本插件作为 Editor 模块，主要在导入管线内部工作。如果你想在 C++ 中控制 MVR Translator 的启用/禁用：

### 头文件引入

```cpp
#include "IDatasmithMVRTranslatorModule.h"
```

### 控制 Translator 启用/禁用

```cpp
// 获取模块引用
IDatasmithMVRTranslatorModule& MVRModule = IDatasmithMVRTranslatorModule::Get();

// 禁用 MVR Translator（恢复默认 Datasmith Native Translator）
MVRModule.SetDatasmithMVRNativeTanslatorEnabled(false);

// 重新启用 MVR Translator
MVRModule.SetDatasmithMVRNativeTanslatorEnabled(true);
```

> **来源**: `IDatasmithMVRTranslatorModule.h` (Public API)

注意：模块启动时默认启用 MVR Translator。调用 `SetDatasmithMVRNativeTanslatorEnabled(false)` 会恢复原始的 `FDatasmithNativeTranslator`。

### 自定义导入流程

如果需要在代码中直接创建 DMX Library（不通过 Datasmith 管线），可以使用 `UDMXLibraryFromMVRFactory`：

```cpp
#include "Factories/DMXLibraryFromMVRFactory.h"
#include "Library/DMXLibrary.h"

UDMXLibraryFromMVRFactory* Factory = NewObject<UDMXLibraryFromMVRFactory>();
bool bCanceled = false;
UObject* Result = Factory->FactoryCreateFile(
    UDMXLibrary::StaticClass(),
    Package,
    FName("MyDMXLibrary"),
    RF_Public | RF_Standalone | RF_Transactional,
    TEXT("/path/to/file.mvr"),
    nullptr,
    GWarn,
    bCanceled
);
UDMXLibrary* DMXLibrary = Cast<UDMXLibrary>(Result);
```

> **来源**: `DatasmithMVRNativeTranslator.cpp` 中 `CreateDMXLibraryFromMVR()` 的逻辑

## 模块依赖

本插件的 `Build.cs` 中使用 `PrivateDependencyModuleNames`（全部为私有依赖），这意味着外部模块**不应直接依赖本插件的模块**：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `AssetRegistry` | 资产注册（创建 DMX Library 后注册到资产系统） |
| `DatasmithContent` | Datasmith 内容类型定义 |
| `DatasmithCore` | Datasmith 核心 API（场景工厂、Metadata 等） |
| `DatasmithNativeTranslator` | 默认的 Datasmith Native Translator（被本插件替换/继承） |
| `DatasmithTranslator` | Datasmith Translator 框架（注册/注销 Translator） |
| `DMXEditor` | DMX 编辑器功能（MVR 导入工厂） |
| `DMXRuntime` | DMX 运行时（MVR Scene Actor、DMX Library） |
| `Engine` | UE 引擎核心 |
| `Slate` | UI 框架（通知消息） |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `DMXEngine` | 提供 DMX Library、MVR 解析、MVR Scene Actor 等核心功能 |
| `DatasmithContent` | Datasmith 内容资产支持 |
| `DatasmithImporter` | Datasmith 导入管线 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2024-09-17 | `4692008` | DMX: Remove experimental and beta flags from DMX plugins. All DMX plugins are now production ready | DMX 相关插件全部摘除实验/Beta 标记，正式进入生产就绪状态 |
| 2024-08-01 | `dca5f14` | Fixed some incorrect TSoftObjectPtr types | 修复 TSoftObjectPtr 类型错误，可能是重构过程中的兼容性修复 |
| 2023-07-24 | `ec0ca35` | DMX - Fix MVR Import with Datasmith file adds DMX Library in content root | 修复 MVR 导入时 DMX Library 被错误放置在 Content 根目录的问题 |

### 维护评价

- **创建时间**: 2022 年 5 月，约 4 年前
- **最新功能性更新**: 2024 年 9 月摘除 Beta 标记，说明已被 Epic 认定为生产就绪
- **更新频率**: 低频（约每年 1-2 次提交），但这是因为插件功能稳定、代码量小
- **活跃度**: 维护中——功能稳定，无已知废弃标记
- **推荐**: ✅ 推荐使用。该插件是 DMX/MVR 工作流在 UE5 中的标准集成方案，已脱离实验状态，且作为 Datasmith 导入管线的透明扩展，使用无需额外代码

**注意**: 本插件仅 6 个源文件，功能聚焦且边界清晰。如果你的工作流不涉及 MVR 文件，此插件不会产生任何影响（只是多注册了一个 Translator）。如果你需要导入 MVR，这是唯一官方支持的路径。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DatasmithMVR)
- [DMXEngine 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine)（提供 MVR 解析、DMX Library、MVR Scene Actor 等核心依赖）
- [DatasmithImporter 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)（Datasmith 导入管线）
