# CodeLite Integration

> Allows access to source code in CodeLite.

| 属性 | 值 |
|---|---|
| 中文名 | CodeLite 集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CodeLiteSourceCodeAccess` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2015-07-14 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/CodeLiteSourceCodeAccess) | |

## 用途

此插件为 Unreal Engine 编辑器提供 [CodeLite](https://codelite.org/) IDE 的源码访问集成。CodeLite 是一款轻量级的跨平台 C/C++ IDE，特别在 Linux 开发者中有一定用户群。

插件通过实现 `ISourceCodeAccessor` 接口，将 UE 编辑器中涉及"打开源文件"的操作（如双击编译错误跳转到代码行、在编辑器内打开解决方案等）路由到 CodeLite，而非默认的 Visual Studio。本质上，它是一个 IDE 桥接层，让习惯使用 CodeLite 的 Linux 开发者无需切换编辑器即可获得流畅的 UE 开发体验。

**重要限制**：此插件仅在 **Linux 平台**上可用（PlatformAllowList: Linux）。

## 使用场景

- 你在 Linux 上使用 CodeLite 作为主力 C++ IDE 进行 UE 项目开发 → 启用此插件，双击编译错误即可在 CodeLite 中定位到对应代码行
- 你的团队使用 CodeLite + UBT（CodeLite 项目生成器）的开发工作流 → 此插件与 UBT 的 CodeLite 项目生成功能配合使用
- 你需要在 UE 编辑器中通过 `Edit > Editor Preferences > Source Code` 切换默认 IDE → 选择 CodeLite 作为源码访问器

## 蓝图用法

此插件不暴露任何蓝图可调用的函数或属性。它作为编辑器源码访问器运行，通过 UE 编辑器的 **Editor Preferences → General → Source Code** 设置面板进行配置和选择。

### 核心节点

无。所有交互均通过编辑器偏好设置完成。

## C++ 用法

### 头文件引入

```cpp
#include "CodeLiteSourceCodeAccessModule.h"
#include "CodeLiteSourceCodeAccessor.h"
```

### 基本用法

该插件遵循 `ISourceCodeAccessor` 接口模式。以下是接口实现的核心方法说明（来源：`Source/CodeLiteSourceCodeAccess/Private/CodeLiteSourceCodeAccessor.h`）：

```cpp
// 检查 CodeLite 是否可用
FCodeLiteSourceCodeAccessor& Accessor = FModuleManager::GetModuleChecked<FCodeLiteSourceCodeAccessModule>("CodeLiteSourceCodeAccess").GetAccessor();

if (Accessor.CanAccessSourceCode())
{
    // CodeLite 可用，可以进行源码操作
}

// 在 CodeLite 中打开解决方案/工作区
Accessor.OpenSolution();

// 在 CodeLite 中打开指定文件并跳转到特定行
Accessor.OpenFileAtLine(TEXT("/Game/Source/MyClass.cpp"), 42, 10);

// 批量打开多个源文件
TArray<FString> Files = {
    TEXT("/Game/Source/File1.cpp"),
    TEXT("/Game/Source/File2.h")
};
Accessor.OpenSourceFiles(Files);

// 保存 CodeLite 中所有打开的文档
Accessor.SaveAllOpenDocuments();
```

### 进阶用法

插件内部使用 `FCriticalSection` 保护解决方案路径的缓存，通过 `Launch()` 方法调用 CodeLite 可执行文件。路径获取通过模块管理器（Module Manager）在主线程完成，避免多线程问题：

```cpp
// 刷新可用性（当 CodeLite 安装状态发生变化时调用）
Accessor.RefreshAvailability();

// 检查解决方案文件是否存在
if (Accessor.DoesSolutionExist())
{
    // 解决方案存在，可以打开
    Accessor.OpenSolutionAtPath(TEXT("/path/to/project.workspace"));
}
```

## Demo 示例

以下是一个最小示例，展示如何在编辑器模块中注册自定义的源码访问器扩展（实际使用中，直接启用插件即可，无需额外代码）：

```cpp
// MyEditorModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "ISourceCodeAccessModule.h"
#include "CodeLiteSourceCodeAccessModule.h"

void FMyEditorModule::StartupModule()
{
    // 通过模块管理器获取 CodeLite 访问器模块
    auto* CodeLiteModule = FModuleManager::GetModulePtr<FCodeLiteSourceCodeAccessModule>("CodeLiteSourceCodeAccess");
    if (CodeLiteModule)
    {
        FCodeLiteSourceCodeAccessor& Accessor = CodeLiteModule->GetAccessor();
        UE_LOG(LogTemp, Log, TEXT("CodeLite accessor available: %s"), 
            *Accessor.GetNameText().ToString());
    }
}

void FMyEditorModule::ShutdownModule()
{
}
```

> **注意**：正常使用只需在 Editor Preferences 中选择 CodeLite 作为源码访问器即可，无需编写任何 C++ 代码。以上示例仅供了解插件 API 结构。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HotReload` | 支持热重载时与 CodeLite 的源码同步 |

无特殊依赖（仅标准 Core/Engine/Slate 等及 HotReload）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-11-07 | `4fb867b8` | PR #4992: [BUGFIX] Codelite gets wrong path to open workspace file | 修复 CodeLite 打开工作区文件时路径错误的 Bug |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复不可达代码的编译警告 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录结构调整 |
| 2022-04-14 | `6f118cb9` | Add ShortNames to Code Access plugins to reduce the pressure on path length. Problem reported on UDN | 为代码访问插件添加短名称以缩短路径长度 |
| 2021-10-13 | `a12d56ff` | Merge from Release-Engine-Staging @ 17791557 to Release-Engine-Test | 从 Staging 分支合并到 Test 分支 |

### 维护评价

**维护不活跃，谨慎使用。**

- 该插件自 **2015 年**创建至今已超过 10 年，属于古老的工具类插件
- 近 5 年的提交均为**维护性修复**（编译警告、路径 Bug、目录结构调整），无功能性更新
- .uplugin 标记为 `IsBetaVersion: true`（实验性），且 `Installed: false`，说明 Epic 从未将其视为正式支持的功能
- 平台限制为 **Linux only**，用户群体极为有限
- 2025 年 11 月的路径修复 Bug 表明插件仍有人在使用和报告问题
- **推荐**：如果你是 Linux 上的 CodeLite 用户，这是一个值得启用的轻量插件；否则无需关注

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/CodeLiteSourceCodeAccess)
- [CodeLite 官方网站](https://codelite.org/)（第三方 IDE，非 Epic 官方文档）