# KDevelop Integration

> Allows access to source code in KDevelop.

| 属性 | 值 |
|---|---|
| 中文名 | KDevelop 集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `KDevelopSourceCodeAccess` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2014-11-04 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/KDevelopSourceCodeAccess) | |

## 用途

为 Linux 平台上的 Unreal Engine 编辑器提供 KDevelop IDE 的源代码访问集成。当开发者在 Linux 上使用 KDevelop 作为主力 IDE 时，此插件允许编辑器直接跳转到源码文件的指定行号，打开解决方案，以及管理项目中的源文件——与 Visual Studio 在 Windows 上的"双击跳转"体验一致。

该插件实现了 `ISourceCodeAccessor` 接口，属于 UE 源代码访问器插件体系的一部分。编辑器会根据用户在设置中选择的 IDE 自动调用对应的访问器插件。

## 使用场景

- 你在 Linux 上使用 KDevelop 作为 UE 项目的 C++ IDE → 启用此插件
- 你希望在蓝图中双击错误信息能直接在 KDevelop 中打开对应源码行 → 此插件提供该能力
- 你需要从编辑器一键打开整个 KDevelop 解决方案 → 使用此插件的 OpenSolution 功能

**限制**：仅在 Linux 平台可用（`PlatformAllowList: ["Linux"]`）。

## 蓝图用法

此插件不暴露任何蓝图接口。所有功能通过编辑器内部的 `ISourceCodeAccessor` 接口自动集成，用户在 **编辑器偏好设置 → Source Code** 中选择 KDevelop 即可激活。

## C++ 用法

此插件作为源代码访问器，通常不需要在 C++ 层面直接使用。以下信息供有兴趣了解或扩展其功能的开发者参考。

### 头文件引入

```cpp
#include "KDevelopSourceCodeAccessor.h"
#include "KDevelopSourceCodeAccessModule.h"
```

### 核心接口

`FKDevelopSourceCodeAccessor` 实现了 `ISourceCodeAccessor` 接口，提供以下能力：

```cpp
// 判断 KDevelop 是否可用
bool CanAccessSourceCode() const;

// 打开 KDevelop 解决方案
bool OpenSolution() override;

// 在 KDevelop 中打开指定文件的指定行
bool OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber = 0) override;

// 在 KDevelop 中打开多个源文件
bool OpenSourceFiles(const TArray<FString>& AbsoluteSourcePaths) override;

// 向项目添加源文件
bool AddSourceFiles(const TArray<FString>& AbsoluteSourcePaths, const TArray<FString>& AvailableModules) override;

// 保存所有打开的文档
bool SaveAllOpenDocuments() const override;
```

### 通过模块访问

```cpp
// 获取模块实例
FKDevelopSourceCodeAccessModule& Module = FModuleManager::Get().LoadModuleChecked<FKDevelopSourceCodeAccessModule>("KDevelopSourceCodeAccess");

// 获取访问器
FKDevelopSourceCodeAccessor& Accessor = Module.GetAccessor();

// 使用访问器
if (Accessor.CanAccessSourceCode())
{
    Accessor.OpenFileAtLine(TEXT("/path/to/file.cpp"), 42, 0);
}
```

来源：`Source/KDevelopSourceCodeAccess/Private/KDevelopSourceCodeAccessModule.h`、`KDevelopSourceCodeAccessor.h`

## Demo 示例

此插件为编辑器工具类，无需用户编写代码。以下展示最小的模块扩展示例：

```cpp
// MySourceCodeAccessor.h
#pragma once

#include "ISourceCodeAccessor.h"

class FMySourceCodeAccessor : public ISourceCodeAccessor
{
public:
    virtual bool CanAccessSourceCode() const override { return true; }
    virtual FName GetFName() const override { return TEXT("MyAccessor"); }
    virtual FText GetNameText() const override { return NSLOCTEXT("MyAccessor", "Name", "My IDE"); }
    virtual FText GetDescriptionText() const override { return NSLOCTEXT("MyAccessor", "Desc", "My custom IDE accessor"); }
    virtual bool OpenSolution() override { /* 实现打开逻辑 */ return true; }
    virtual bool OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber) override { /* 实现跳转逻辑 */ return true; }
    virtual bool SaveAllOpenDocuments() const override { return true; }
    virtual void Tick(const float DeltaTime) override { }
};
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

内部依赖了 `HotReload` 模块，用于在热重载时协调 IDE 状态。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件批量更新 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件内链接更新为安全协议 |
| 2022-04-14 | `6f118cb9` | Add ShortNames to Code Access plugins to reduce the pressure on path length. Problem reported on UDN | 为源码访问器插件添加短名称以缓解路径过长问题 |
| 2021-10-13 | `a12d56ff` | Merge from Release-Engine-Staging @ 17791557 to Release-Engine-Test | 从 Staging 分支合并到 Test 分支 |

### 维护评价

该插件自 2014 年创建以来已有 12 年历史，属于成熟的基础设施级插件。近 3 年的更新全部为编译器适配、路径优化和格式清理等维护性改动，**无任何功能性更新**。最后一次实质性代码变更可追溯至 2018 年之前。

考虑到以下因素：
- 功能已完整且稳定，无需频繁更新
- 仅限 Linux 平台，用户群体较小
- KDevelop IDE 本身用户群体在缩小
- 作为 UncookedOnly 模块，不影响打包后的产品

**推荐使用**：如果你在 Linux 上使用 KDevelop，此插件开箱即用，无需顾虑。它属于"稳定且不需要更新"的类型。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/KDevelopSourceCodeAccess)
- [KDevelop 官网](https://www.kdevelop.org/)