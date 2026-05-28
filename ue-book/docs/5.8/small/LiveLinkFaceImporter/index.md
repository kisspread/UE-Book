# Live Link Face Importer

> Imports CSV recordings from the Live Link Face app.

| 属性 | 值 |
|---|---|
| 中文名 | Live Link Face 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产） |
| 模块 | `LiveLinkFaceImporter` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LiveLinkFaceImporter) | |

## 用途

该插件用于将 Epic 的 **Live Link Face** iOS 应用导出的 CSV 格式的面部动捕数据导入到 Unreal Engine 中。Live Link Face 是一款利用 iPhone 的 TrueDepth 摄像头进行面部动作捕捉的应用。此插件解决的核心问题是将这些录制的 CSV 文件转换为引擎可用的 Live Link 数据，以便驱动 MetaHuman 或其它角色的面部动画。

## 使用场景

- 你使用 Live Link Face 应用录制了演员的面部表情数据，并希望将其作为动画资产在 Unreal Engine 中回放或编辑。
- 你需要将录制的 CSV 数据转换为可用于动画蓝图或序列器驱动面部 Morph Target 的数据。

## 蓝图用法

该插件主要是一个**编辑器工厂类**，提供文件导入功能，不包含用于运行时蓝图调用的公开节点。

### 核心功能

用户可以在 Unreal Editor 的 **Content Browser** 中通过 **Import** 按钮或直接拖放 CSV 文件来触发导入。插件会自动识别 `.csv` 文件。

**使用示例**：
1. 在 Content Browser 中，右键点击空白处，选择 `Import to /Game/...`。
2. 在文件选择器中，选择从 Live Link Face 应用导出的 `.csv` 文件。
3. 插件会自动将 CSV 数据转换为一个 **LiveLinkSubjectPreset** 资产，并将其保存到指定位置。
4. 该预设资产可在 **Live Link** 面板中查看和使用，用于驱动角色动画。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkFaceImporterFactory.h"
```

### 基本用法

该插件的核心是 `ULiveLinkFaceImporterFactory` 类，它继承自 `UFactory`。在 C++ 中直接使用它的场景较少，因为其主要设计是作为编辑器数据导入的抽象层。

如果你想在 C++ 中以编程方式触发 CSV 文件的解析和导入逻辑，可以创建一个工厂实例并调用其方法，但请注意，`FactoryCreateText` 方法通常由引擎的导入框架调用。

**头文件分析**:
- `FactoryCanImport`: 判断是否可以导入指定文件。
- `FactoryCreateText`: 执行实际的文本导入操作，将 CSV 内容解析为 UE 对象。
- `LoadCSV`, `CreateSubjectString`, `ParseTimecode`, `InferFrameRate`: 内部辅助函数，用于处理 CSV 文件。

### 进阶用法

由于这是编辑器插件，通常不会在运行时 C++ 代码中使用。其“进阶用法”更多体现在理解其内部工作原理，以便在需要时进行扩展或调试。

## Demo 示例

该插件没有独立的运行时 Demo。其使用方式完全集成在 Unreal Editor 的资产导入流程中。

一个最小化的“概念性” C++ 调用（非官方推荐用法，仅用于展示）：

```cpp
// MyImporter.cpp
#include "LiveLinkFaceImporterFactory.h"
#include "Misc/FileHelper.h"

void ImportLiveLinkFaceCSV(const FString& FilePath, UObject* InParent, const FName& AssetName)
{
    // 1. 读取文件内容
    FString FileContent;
    FFileHelper::LoadFileToString(FileContent, *FilePath);

    // 2. 创建工厂实例
    ULiveLinkFaceImporterFactory* Factory = NewObject<ULiveLinkFaceImporterFactory>();

    // 3. 检查是否可导入
    if (Factory->FactoryCanImport(FilePath))
    {
        // 4. 准备导入参数
        const TCHAR* Buffer = *FileContent;
        const TCHAR* BufferEnd = Buffer + FileContent.Len();
        FFeedbackContext Warn;

        // 5. 调用导入函数（注意：这通常由编辑器框架内部调用）
        UObject* ImportedObject = Factory->FactoryCreateText(
            ULiveLinkSubjectPreset::StaticClass(), // 假设目标类，实际需根据实现确定
            InParent,
            AssetName,
            RF_Public | RF_Transactional,
            nullptr,
            TEXT("csv"),
            Buffer,
            BufferEnd,
            &Warn
        );

        if (ImportedObject)
        {
            UE_LOG(LogTemp, Log, TEXT("Successfully imported Live Link Face preset: %s"), *AssetName.ToString());
        }
    }
}
```
**注意**：以上代码仅为示意，`FactoryCreateText` 的目标类 (`UClass* InClass`) 参数取决于插件内部的具体实现，可能并非直接是 `ULiveLinkSubjectPreset`。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心依赖，用于创建和管理 Live Link 主体和预设。 |
| `Core`, `CoreUObject`, `Engine` | 引擎基础模块（已省略）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式 UE_LOG 宏迁移至 UE_LOGF 宏。 |
| 2024-06-27 | `a890c0ce` | Fixed some 'deprecated' FString usage. | 修复了一些已废弃的 FString 用法。 |
| 2023-08-05 | `99b2b2c0` | Add 30FPS support to LiveLinkFaceImporter and remove platform restriction | 为 LiveLinkFaceImporter 添加 30FPS 支持，并移除平台限制。 |
| 2023-07-27 | `912b34bd` | Undo //UE5/Release-5.3/Engine/Plugins/Experimental/LiveLinkFaceImporter/... changelist 26640196 | 撤销了上一次改动。 |
| 2023-07-27 | `e07a86f7` | Add 30FPS support to LiveLinkFaceImporter and remove platform restrictions | 为 LiveLinkFaceImporter 添加 30FPS 支持，并移除平台限制（首次提交，后被撤销）。 |

### 维护评价

- **活跃度**：插件创建于 2022 年，最新实质性功能更新（添加 30FPS 支持）在 2023 年 8 月。之后的更新主要是代码维护（修复废弃用法、迁移日志宏）和一次错误修复/回滚。
- **状态**：插件自 2023 年 8 月后没有新的功能添加，处于**维护不活跃**状态。
- **已知问题/限制**：作为实验性 (`IsBetaVersion: true`) 插件，可能未经过广泛测试。它依赖于特定格式的 CSV 文件，Live Link Face 应用输出格式的变化可能导致其失效。
- **推荐程度**：适用于需要快速将 Live Link Face 录制数据导入引擎的**原型开发或特定工作流**。对于生产项目，应评估其长期维护状态，并考虑直接使用 Live Link 的实时传输功能或寻找其他经过验证的导入方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LiveLinkFaceImporter)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/live-link-face-app-documentation) (Live Link Face 应用相关文档，非本插件专属)