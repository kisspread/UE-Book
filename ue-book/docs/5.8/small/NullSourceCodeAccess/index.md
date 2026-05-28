# NullSourceCodeAccess

> Allows access to c++ projects while only looking for clang++

| 属性 | 值 |
|---|---|
| 中文名 | Linux编译器集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `NullSourceCodeAccess` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2015-04-21 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NullSourceCodeAccess) | |

## 用途

这个插件为 **Linux 平台**提供一个“空”或“默认”的源代码访问器实现。它主要解决在 Linux 环境下，当开发者仅使用 `clang++` 进行编译，而没有配置或不想使用特定 IDE（如 Qt Creator, VS Code 等）时，UE 编辑器仍然能够知道“源代码是可访问的”，从而启用依赖于源代码访问的各种编辑器功能（例如，双击错误跳转、在编辑器内添加新 C++ 类等）。它充当了一个不与任何外部编辑器绑定的默认回退方案。

## 使用场景

- 你正在 **Linux** 系统上进行 UE5 开发。
- 你主要使用命令行或 Makefile 与 `clang++` 编译器进行交互，不使用或未安装 Qt Creator、VS Code 等集成的 IDE。
- 你希望 UE 编辑器的基础 C++ 功能（如创建新类、打开文件）能正常工作，而不需要绑定一个特定的外部代码编辑器。

## 蓝图用法

此插件是一个底层的开发者工具模块，**不包含任何公开的蓝图（BlueprintCallable/BlueprintReadWrite）API**。它的作用是通过实现 `ISourceCodeAccessor` 接口，在编辑器内部集成，无需在蓝图中直接调用。

## C++ 用法

此插件的核心是实现 `ISourceCodeAccessor` 接口，并将其注册为默认的源代码访问器。它通常不需要使用者直接在项目代码中调用。

### 头文件引入

作为引擎插件，无需在项目中直接引入。其行为通过引擎的源代码访问器子系统生效。

### 基本用法（插件内部实现）

该插件的核心是 `FNullSourceCodeAccessor` 类。它实现了 `ISourceCodeAccessor` 接口，但大部分方法为空操作或返回成功状态，仅用于确认源代码是“可用”的。

**文件路径：** `Engine/Plugins/Developer/NullSourceCodeAccess/Private/NullSourceCodeAccessor.h`

```cpp
// FNullSourceCodeAccessor 的关键实现
class FNullSourceCodeAccessor : public ISourceCodeAccessor
{
public:
    // 检查是否可以访问源代码。对于此插件，始终返回 true。
    virtual bool CanAccessSourceCode() const override { return true; }

    // 返回此访问器的标识名称
    virtual FName GetFName() const override;

    // 打开解决方案文件 - 此实现中为空操作
    virtual bool OpenSolution() override { return false; }

    // 在特定行打开文件 - 此实现中为空操作
    virtual bool OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber = 0) override { return false; }

    // ... 其他接口方法均为空操作或返回默认值
};
```

### 进阶用法（模块注册）

插件模块 `FNullSourceCodeAccessModule` 在启动时创建 `FNullSourceCodeAccessor` 实例，并将其注册到引擎的源代码访问器系统中，作为默认选项之一。

**文件路径：** `Engine/Plugins/Developer/NullSourceCodeAccess/Private/NullSourceCodeAccessModule.h`

```cpp
class FNullSourceCodeAccessModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    FNullSourceCodeAccessor& GetAccessor() { return NullSourceCodeAccessor; }

private:
    FNullSourceCodeAccessor NullSourceCodeAccessor;
};
```

通常，当其他更具体的源代码访问器（如用于特定 IDE 的）不可用或未激活时，系统会回退到使用此类“null”访问器。

## Demo 示例

此插件本身是一个功能性的工具插件，无需创建额外的示例。要观察其效果，可以在一个纯 Linux 环境下（不安装 Qt Creator 等 UE 官方支持的 IDE），观察 UE 编辑器是否仍然允许你创建 C++ 类并打开文件（虽然文件可能不会在外部编辑器中打开，但操作本身会成功）。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的 `Build.cs` 文件未列出任何不常见的依赖模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录的常规格式调整或构建系统更新。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的外部链接更新为使用安全协议（如 HTTPS）。 |
| 2022-04-14 | `6f118cb9` | Add ShortNames to Code Access plugins to reduce the pressure on path length. Problem reported on UDN | 为源代码访问器插件添加短名称，以解决路径长度过长的问题。 |

### 维护评价

这是一个**功能极其简单且稳定**的工具插件，创建于 2015 年（约 9 年前）。其最后一次实质性代码改动（添加 ShortNames）在 2022 年，之后仅有一次无关紧要的目录结构更新。由于其功能单一且自包含，很少需要更新。它**仍然被默认启用**，表明其对于支持 Linux 命令行开发工作流是必要的。尽管更新不频繁，但因其功能固化，**不存在明显的已知问题或限制**。对于在 Linux 上进行纯命令行编译的开发者，推荐保持其启用状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NullSourceCodeAccess)
- 官方文档：无
- 测试用例：无独立测试文件