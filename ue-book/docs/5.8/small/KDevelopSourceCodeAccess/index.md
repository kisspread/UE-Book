# KDevelop Integration

> Allows access to source code in KDevelop.

| 属性 | 值 |
|---|---|
| 中文名 | KDevelop集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `KDevelopSourceCodeAccess` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2014-11-04 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/KDevelopSourceCodeAccess) | |

## 用途

该插件为 **Linux 平台**上的 Unreal Editor 提供了与 **KDevelop IDE** 的集成。它的核心作用是实现编辑器内置的“在 IDE 中打开文件”功能，但底层调用的是 KDevelop 而非 Visual Studio 或 Xcode。这解决了开发者在 Linux 环境下使用 KDevelop 进行 UE5 C++ 开发时的代码导航问题，使编辑器能直接将文件打开并定位到指定代码行，极大地提升了开发效率。

## 使用场景

- **你在 Linux 上使用 KDevelop 作为主 IDE 进行 UE5 插件或游戏开发**：当你需要在编辑器中快速查看某个蓝图节点背后的 C++ 实现，或调试时跳转到报错代码处，该插件会自动启动 KDevelop 并打开对应文件。

## 蓝图用法

该插件是编辑器源代码访问的基础架构插件，不包含任何可直接在蓝图中调用的节点。其功能通过编辑器的源代码访问器设置自动生效。

## C++ 用法

### 核心接口

该插件的核心是 `FKDevelopSourceCodeAccessor` 类，它实现了引擎的 `ISourceCodeAccessor` 接口。开发者通常不直接与之交互，而是通过编辑器设置将其配置为默认的源代码访问器。

### 基本用法

当插件被激活且 KDevelop 可用时，引擎会使用它来处理所有“打开源代码”的请求。

```cpp
// 引用自 Source/KDevelopSourceCodeAccess/Private/KDevelopSourceCodeAccessor.h
// 该类被模块管理器实例化，并在编辑器设置中选择“KDevelop”后生效。
// 核心功能通过实现 ISourceCodeAccessor 的纯虚函数来完成：

// 1. 检查IDE是否可用
virtual bool CanAccessSourceCode() const override;

// 2. 在IDE中打开文件并跳转到特定行和列
virtual bool OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber = 0) override;

// 3. 打开UE5的解决方案文件 (.pro)
virtual bool OpenSolution() override;
```

### 模块使用示例

如果你需要在自己的模块中以编程方式使用该源代码访问器，可以这样做：

```cpp
// 引用自 Source/KDevelopSourceCodeAccess/Private/KDevelopSourceCodeAccessModule.h
#include "KDevelopSourceCodeAccessModule.h"
#include "KDevelopSourceCodeAccessor.h"

// 获取 KDevelop 访问器模块
FKDevelopSourceCodeAccessModule& Module = FModuleManager::Get().LoadModuleChecked<FKDevelopSourceCodeAccessModule>("KDevelopSourceCodeAccess");

// 获取具体的访问器实例
FKDevelopSourceCodeAccessor& Accessor = Module.GetAccessor();

// 现在可以使用访问器的功能，例如尝试打开一个文件
if (Accessor.CanAccessSourceCode())
{
    Accessor.OpenFileAtLine(TEXT("/path/to/your/SourceFile.cpp"), 42, 10);
}
```

## Demo 示例

一个最小的编辑器模块，展示了如何尝试使用 KDevelop 源代码访问器。

**MyEditorModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnOpenTestFile();
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "KDevelopSourceCodeAccessModule.h"
#include "KDevelopSourceCodeAccessor.h"

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    // 可以注册一个控制台命令来测试
    IConsoleManager::Get().RegisterConsoleCommand(
        TEXT("MyModule.OpenTestInKDevelop"),
        TEXT("Opens a test file using the KDevelop source accessor."),
        FConsoleCommandDelegate::CreateRaw(this, &FMyEditorModule::OnOpenTestFile)
    );
}

void FMyEditorModule::ShutdownModule()
{
}

void FMyEditorModule::OnOpenTestFile()
{
    // 尝试加载 KDevelop 访问器模块
    if (FModuleManager::Get().IsModuleLoaded("KDevelopSourceCodeAccess"))
    {
        FKDevelopSourceCodeAccessModule& KDevelopModule = FModuleManager::Get().LoadModuleChecked<FKDevelopSourceCodeAccessModule>("KDevelopSourceCodeAccess");
        FKDevelopSourceCodeAccessor& Accessor = KDevelopModule.GetAccessor();

        if (Accessor.CanAccessSourceCode())
        {
            // 尝试打开此模块自身的头文件，跳转到第一行
            FString MyHeaderPath = FPaths::ProjectPluginsDir() / TEXT("MyPlugin/Source/MyEditorModule/Public/MyEditorModule.h");
            Accessor.OpenFileAtLine(MyHeaderPath, 1);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("KDevelop is not available."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("KDevelopSourceCodeAccess module is not loaded."));
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

## 模块依赖

从模块构建文件分析，使用者无需直接依赖此插件。该插件通过引擎的 `ISourceCodeAccessor` 接口被集成。如果其他模块需要调用它，应确保：

| 模块 | 用途 |
|---|---|
| `KDevelopSourceCodeAccess` | 提供 KDevelop 源代码访问器的实现 |
| `HotReload` | 模块构建依赖，用于支持编辑器内的代码热重载功能 |

**说明**：该插件本身依赖 `HotReload` 模块，因为源代码访问器功能与开发时的代码编译和重载紧密相关。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏更新为新的 UE_LOGF 宏，属于代码质量维护。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件的通用批量更新，无具体功能说明。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件的供应商链接更新为 HTTPS，安全维护。 |
| 2022-04-14 | `6f118cb9` | Add ShortNames to Code Access plugins to reduce the pressure on path length. Problem reported on UDN | 为代码访问器插件添加简称，以缓解因路径过长导致的问题。 |
| 2021-10-13 | `a12d56ff` | Merge from Release-Engine-Staging @ 17791557 to Release-Engine-Test | 引擎发布分支间的合并，无具体功能说明。 |

### 维护评价

- **创建时间**：创建于 2014 年，是 UE4 早期为 Linux 开发环境添加的插件，历史悠久。
- **最近更新频率和内容**：最近一次有实质意义的更新是 2022 年添加简称（`6f118cb9`）。之后的更新均为被动维护，如合并分支、安全协议更新和日志宏迁移。
- **是否还在活跃维护**：**不活跃**。该插件功能稳定且单一，没有新的功能需求或重大 Bug 修复，处于“维持可运行”状态。
- **是否推荐使用**：如果你**在 Linux 平台上使用 KDevelop 作为 Unreal 的 IDE**，此插件仍然有用且可用。但对于新项目，考虑到 KDevelop 在 UE 社区的流行度低于 VS Code/CLion，其必要性可能不高。该插件本身稳定，可以信赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/KDevelopSourceCodeAccess)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）