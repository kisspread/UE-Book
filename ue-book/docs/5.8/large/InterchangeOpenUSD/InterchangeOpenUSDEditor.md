# Interchange OpenUSD

> Allows translation of OpenUSD files via the Interchange framework

| 属性 | 值 |
|---|---|
| 中文名 | OpenUSD 互换翻译器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、设置自定义） |
| 模块 | `InterchangeOpenUSDEditor` (Runtime), `InterchangeOpenUSDImport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD) | |

## 用途

InterchangeOpenUSD 是 UE5 Interchange 框架的 USD 扩展插件，为 Interchange 资产交换管线提供对 OpenUSD（Universal Scene Description）格式文件的翻译支持。

该插件解决的核心问题：
- **USD 文件导入**：通过 Interchange 统一导入管线，将 `.usd`、`.usda`、`.usdc`、`.usdz` 文件转换为 UE5 内部资产格式（网格体、材质、骨骼等）
- **可扩展的 Schema 处理器**：采用模块化的 Schema Handler 机制，允许用户自定义 USD 各种 Schema 的处理优先级和行为
- **材质翻译**：支持 MaterialX 材质翻译，正确处理实例内部材质的去重
- **骨骼与物理资产**：支持 USD Skeleton 和 PhysicsAssets 的跟踪与导入

与其他 USD 插件不同，本插件专注于作为 Interchange 管线的一个翻译器（Translator）运行，而非独立的导入系统。

## 使用场景

- 你需要将 USD 格式的影视资产（来自 Houdini、Maya、Blender 等 DCC 工具）导入 UE5 → 启用本插件
- 你需要通过蓝图或 C++ 自动化 USD 导入流程 → 使用 Interchange 管线的 USD 翻译器
- 你需要自定义 USD Schema 的处理顺序（例如优先处理 MaterialX 材质）→ 配置 Schema Handler 顺序
- 你使用 USDZ 格式的 AR 资产 → 本插件支持 USDZ 文件处理
- 你需要精细控制 USD 导入的渲染上下文和材质用途 → 自定义 Translator Settings

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Default Schema Handler Entries` | 获取默认的 Schema 处理器列表，可修改后设置到 TranslatorSettings | `UInterchangeUsdTranslatorBlueprintLibrary` |

### 使用示例（蓝图描述）

**自定义 Schema Handler 顺序：**

1. 调用 `Get Default Schema Handler Entries` 节点获取当前注册的处理器列表
2. 将返回的 `TArray<FSchemaHandlerEntry>` 连接到数组操作节点（如 Filter、Sort）
3. 修改处理器顺序或过滤不需要的处理器
4. 获取 `UInterchangeUsdTranslatorSettings` 的 Class Default Object
5. 将修改后的数组设置到该对象的 `CustomHandlerEntries` 属性
6. 后续所有 USD 导入操作将使用自定义的处理器顺序

**使用默认设置导入 USD 文件：**

1. 使用 `Interchange Import Asset` 或类似的 Interchange 导入节点
2. 指定 USD 文件路径
3. Interchange 框架会自动检测文件格式并使用 USD Translator 进行翻译

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeUsdTranslatorBlueprintLibrary.h"
#include "InterchangeUsdTranslatorSettings.h"  // 来自 Import 模块
```

### 基本用法 - 获取并修改 Schema Handler 列表

```cpp
// 获取默认 Schema Handler 列表
TArray<FSchemaHandlerEntry> HandlerEntries = UInterchangeUsdTranslatorBlueprintLibrary::GetDefaultSchemaHandlerEntries();

// 自定义处理器顺序
// 可以重新排列、过滤 HandlerEntries
TArray<FSchemaHandlerEntry> CustomEntries;
for (const FSchemaHandlerEntry& Entry : HandlerEntries)
{
    // 示例：跳过不需要的处理器
    // if (Entry.SchemaName == TEXT("SomeSchema")) continue;
    CustomEntries.Add(Entry);
}

// 设置自定义列表到 Translator Settings
UInterchangeUsdTranslatorSettings* Settings = GetMutableDefault<UInterchangeUsdTranslatorSettings>();
Settings->CustomHandlerEntries = CustomEntries;
```

*来源：`Public/InterchangeUsdTranslatorBlueprintLibrary.h`*

### 进阶用法 - 在编辑器中显示处理器顺序配置窗口

```cpp
// 编辑器中可以调用静态方法显示处理器顺序配置 UI
UInterchangeUsdTranslatorSettings* Settings = GetMutableDefault<UInterchangeUsdTranslatorSettings>();
bool bChanged = SInterchangeUsdHandlerOrderWindow::ShowWindow(Settings);

if (bChanged)
{
    // 用户修改了处理器顺序，重新翻译会使用新配置
    // bNeedNewTranslation 会在窗口关闭时返回
}
```

*来源：`Private/InterchangeUsdHandlerOrderWindow.h`*

## Demo 示例

### 自定义 USD Schema Handler 配置

```cpp
// InterchangeUsdCustomHandlerExample.h
#pragma once

#include "CoreMinimal.h"

class FUsdCustomHandlerExample
{
public:
    /** 配置自定义的 USD Schema Handler 顺序 */
    static void ConfigureCustomSchemaHandlers();
    
    /** 使用自定义配置导入 USD 文件 */
    static bool ImportUsdFile(const FString& FilePath);
};
```

```cpp
// InterchangeUsdCustomHandlerExample.cpp
#include "InterchangeUsdCustomHandlerExample.h"
#include "InterchangeUsdTranslatorBlueprintLibrary.h"
#include "InterchangeUsdTranslatorSettings.h"

void FUsdCustomHandlerExample::ConfigureCustomSchemaHandlers()
{
    // 1. 获取默认处理器列表
    TArray<FSchemaHandlerEntry> DefaultEntries = 
        UInterchangeUsdTranslatorBlueprintLibrary::GetDefaultSchemaHandlerEntries();

    UE_LOG(LogTemp, Log, TEXT("Found %d default schema handlers"), DefaultEntries.Num());
    for (const FSchemaHandlerEntry& Entry : DefaultEntries)
    {
        UE_LOG(LogTemp, Log, TEXT("  Handler: %s"), *Entry.SchemaName);
    }

    // 2. 设置自定义处理器列表到全局设置
    UInterchangeUsdTranslatorSettings* TranslatorSettings = 
        GetMutableDefault<UInterchangeUsdTranslatorSettings>();
    
    if (TranslatorSettings)
    {
        // 保留所有默认处理器，按需调整顺序
        TranslatorSettings->CustomHandlerEntries = DefaultEntries;
    }
}

bool FUsdCustomHandlerExample::ImportUsdFile(const FString& FilePath)
{
    if (!FPaths::FileExists(FilePath))
    {
        UE_LOG(LogTemp, Warning, TEXT("USD file not found: %s"), *FilePath);
        return false;
    }

    // 确保使用自定义配置
    ConfigureCustomSchemaHandlers();

    // 使用 Interchange 管线导入（伪代码，实际取决于完整 API）
    // UInterchangeManager::Get()->ImportAsset(FilePath, ...);
    
    UE_LOG(LogTemp, Log, TEXT("USD import initiated for: %s"), *FilePath);
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架核心模块 |
| `InterchangeNodes` | Interchange 节点定义 |
| `InterchangeEngine` | Interchange 导入引擎 |
| `UsdUtilities` | USD 工具库，提供 USD 基础功能 |
| `Usd` | USD 核心运行时支持 |

> 注意：依赖关系基于典型的 Interchange + USD 插件结构推断，完整依赖请参考 `Source/Editor/InterchangeOpenUSDEditor.build.cs` 和 `Source/Import/InterchangeOpenUSDImport.build.cs`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | 实现骨骼和物理资产的 USD Pregen 跟踪 |
| 2026-05-22 | `e55b6ad4` | USD Pregen: Fix handling of USDZ files. | 修复 USDZ 文件的 Pregen 处理问题 |
| 2026-05-19 | `fd496b57` | USD Pregen: Properly tag nodes produced by MaterialX translator with corresponding prim path so that | MaterialX 翻译器正确标记节点的 USD Prim 路径 |
| 2026-05-14 | `561d9c2d` | USD Pregen: Fix materials inside instances not being deduplicated; | 修复实例内材质未被去重的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的警告 |

### 维护评价

- **活跃开发中**：最近的提交集中在 USD Pregen（预生成）功能的完善，表明该功能正在积极开发
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion: true`，`EnabledByDefault: false`，需要手动启用
- **近期改动方向**：
  - USDZ 文件支持修复
  - MaterialX 材质翻译改进
  - 骨骼和物理资产支持新增
  - 实例化材质去重优化
- **已知限制**：
  - 实验性功能，API 可能变化
  - 需要手动启用插件
  - 依赖 USD 核心插件（可能需要额外启用）
- **推荐使用**：适合需要通过 Interchange 管线导入 USD 资产的项目，但需注意实验性风险。对于生产环境，建议充分测试后再使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD)
- [Interchange 框架文档](https://docs.unrealengine.com/5.0/en-US/interchange-framework-in-unreal-engine/)
- [USD 插件目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/USD)