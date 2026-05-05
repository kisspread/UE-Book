# Python Automation Test

> Enables running Python test scripts (test_*.py) as UE automation tests, with support for latent commands and a built-in test framework.

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ❌ 否（EnabledByDefault: false） |
| 包含内容 | ✅ 是（含 Python 脚本） |
| 模块 | PythonAutomationTest (Editor) |
| 创建时间 | 2019-08-15 |
| 年龄标签 | 👴 老古董（~6.7 年） |
| IsBetaVersion | ✅ 是 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/PythonAutomationTest) | |

## 用途

这个 plugin 桥接了 UE 的 Automation Test 框架和 Python 脚本系统，让你可以用 Python 编写自动化测试并在编辑器的 Session Frontend / Automation 面板中运行。

核心机制：
1. **扫描** 项目 `Content/Python/` 和所有启用 plugin 的 `Content/Python/` 目录，查找 `test_*.py` 文件
2. **注册** 每个找到的 Python 文件为一个 UE automation test（路径 `Editor.Python.{ModuleName}.{filename}`）
3. **执行** Python 文件，并通过 `AutomationScheduler` 支持异步/latent 命令（每个 editor tick 执行一步）
4. **超时** 默认 300 秒，可通过 API 调整

**为什么存在？** UE 原生的 C++ automation test 编写门槛高、迭代慢。这个 plugin 让团队可以用 Python 快速编写编辑器自动化测试，特别适合工具链验证、资产管线测试等场景。

## 使用场景

- 你需要在 CI/CD 中用 Python 脚本验证编辑器功能 → 用这个 plugin
- 你需要测试需要多帧等待的异步操作（如关卡加载、资产导入）→ 用 `AutomationScheduler` 的 latent command
- 你想在 Session Frontend 面板中一键运行 Python 测试 → 这个 plugin 自动注册为 automation test

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIsRunningPyLatentCommand` | 标记是否正在运行 Python latent command | `UPyAutomationTestLibrary` |
| `GetIsRunningPyLatentCommand` | 查询是否正在运行 latent command | `UPyAutomationTestLibrary` |
| `SetPyLatentCommandTimeout` | 设置 latent command 超时（秒） | `UPyAutomationTestLibrary` |
| `GetPyLatentCommandTimeout` | 获取当前超时设置 | `UPyAutomationTestLibrary` |
| `ResetPyLatentCommand` | 重置 latent command 状态和超时 | `UPyAutomationTestLibrary` |

> 这些蓝图节点主要供内部机制使用。日常使用 Python 测试时，你不需要直接调用它们——`AutomationScheduler` Python API 已封装好。

## C++ 用法

### 头文件引入

```cpp
#include "PythonAutomationTest.h"
```

### 内部机制（供参考）

该 plugin 内部定义了一个 latent automation command `FIsRunningPyLatentCommand`，用于在测试运行期间轮询 Python 侧的完成状态：

```cpp
// 定义 latent command（plugin 内部实现）
DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FIsRunningPyLatentCommand, float, Timeout);

bool FIsRunningPyLatentCommand::Update()
{
    float NewTime = FPlatformTime::Seconds();
    if (NewTime - StartTime < Timeout)
    {
        return !UPyAutomationTestLibrary::GetIsRunningPyLatentCommand();
    }
    // 超时处理...
    return true;
}
```

### 测试扫描逻辑

`FPythonAutomationTest` 是一个 Complex Automation Test，它的 `GetTests()` 会扫描两个位置：
1. **项目目录**: `{ProjectContentDir}/Python/test_*.py`
2. **所有启用的 Plugin 目录**: `{PluginContentDir}/Python/test_*.py`（跳过 `site-packages`）

## Python 用法

### 创建测试文件

在项目的 `Content/Python/` 目录下创建以 `test_` 开头的 Python 文件：

```
MyProject/
├── Content/
│   └── Python/
│       └── test_my_feature.py    ← 自动被发现并注册为 automation test
```

### 基本测试模式

```python
import unreal
from automation_test.unittest_utilities import *

runner = TestRunner()

@runner.add_test
def test_something():
    expect(unreal.MathLibrary.abs_int(-5)).to_return(5)

runner.run_all()
```

### Latent（异步）测试

当测试需要等待多帧完成时（如加载关卡、等待异步操作），使用 `AutomationScheduler`：

```python
import unreal

@unreal.AutomationScheduler.add_latent_command
def test_import_asset():
    # 每个 yield 会等待一个 editor tick
    yield unreal.EditorAssetLibrary.load_asset("/Game/MyAsset")
    # 可以嵌套：yield 一个 generator
    yield check_asset_loaded()

def check_asset_loaded():
    # 这个 generator 会在后续 tick 中逐步执行
    asset = unreal.EditorAssetLibrary.load_asset("/Game/MyAsset")
    assert asset is not None
    yield  # 等一帧
```

### 超时设置

```python
# 默认 300 秒，可自定义
unreal.AutomationScheduler.set_latent_command_timeout(600)  # 10 分钟
```

## 测试工具库 (`automation_test`)

Plugin 内置了一套 Python 测试工具（`Content/Python/automation_test/unittest_utilities.py`）：

### TestRunner

测试收集器和运行器，支持生命周期钩子：

```python
runner = TestRunner()

@runner.set_before_all
def setup():
    # 所有测试前执行
    pass

@runner.set_before_each
def setup_each():
    # 每个测试前执行
    pass

@runner.add_test
def my_test():
    pass

runner.run_all()
```

### Expectation API

链式断言风格：

```python
# 函数返回值断言
expect(my_func, arg1, arg2).to_return(expected_value)
expect(my_func, arg1).not_to_return(bad_value)
expect(my_func).to_be_greater_than(10)
expect(my_func).to_have_length(3)
expect(my_func).to_contain(item)
expect(my_func).to_exist()  # not None

# 值断言
expect(some_value).to_be(expected)
expect_true(condition)
expect_false(condition)
```

### 平台过滤

```python
from automation_test.unittest_utilities import *

@test_on_win
@runner.add_test
def test_windows_only():
    pass

@test_on_mac
@runner.add_test
def test_mac_only():
    pass

# 或者多平台
@test_on_platforms(Platform.WIN, Platform.LINUX)
@runner.add_test
def test_cross_platform():
    pass
```

### 预期错误日志

```python
@add_expected_log_error("Some expected warning", count=2)
@runner.add_test
def test_with_expected_errors():
    # 这个测试中产生的匹配日志不会导致测试失败
    pass
```

### 辅助工具

```python
# 生成唯一路径（避免测试间冲突）
path = unique_path("/Game/TestAsset")  # → "/Game/TestAsset_a1b2c3d4..."

# 安全删除文件（带重试）
try_remove_file("/path/to/file")

# 递归清理目录
remove_dir_sync("/path/to/dir")
```

## Demo 示例

### 完整的最小测试文件

```python
# Content/Python/test_example.py
import unreal
from automation_test.unittest_utilities import *

runner = TestRunner()

@runner.add_test
def test_create_asset():
    """测试创建一个 DataAsset"""
    asset_path = unique_path("/Game/Tests/TestAsset")
    asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "TestAsset", "/Game/Tests", unreal.DataAsset, unreal.DataAssetFactory()
    )
    expect(asset).to_exist()

@runner.add_test
def test_editor_utils():
    """测试编辑器工具函数"""
    expect(unreal.EditorAssetLibrary.does_asset_exist, "/Game/Tests/TestAsset").to_return(True)

@add_expected_log_error("Test warning pattern")
@runner.add_test
def test_expected_warning():
    """测试预期会产生警告的操作"""
    pass

runner.run_all()
```

在 Session Frontend → Automation 面板中，你会看到 `Python.test_example.test_create_asset` 等测试项。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Projects` | 项目信息查询（获取 Content 目录） |
| `UnrealEd` | 编辑器功能 |
| `EditorFramework` | 编辑器框架（Private） |
| `PythonScriptPlugin` | Python 脚本执行引擎（Private） |

**Plugin 依赖**:
- `PythonScriptPlugin` — Python 脚本引擎，必须启用
- `FunctionalTestingEditor` — 功能测试编辑器支持

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-05-30 | `2739c3d` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n | 批量代码修正，非功能性更新 |
| 2024-11-09 | `66e9bb3` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理废弃宏，非功能性更新 |
| 2023-06-13 | `06817dd` | Avoid looking for tests in plugin content python site-packages folder | 修复扫描逻辑，跳过 site-packages 目录中的文件 |

### 维护评价

- **状态**: ⚠️ 维护不活跃
- 最近一次功能性更新在 **2023 年 6 月**（跳过 site-packages 的修复），之后均为批量代码清理
- 仍标记为 **Beta**（IsBetaVersion: true），6 年多未"毕业"
- 核心功能稳定（Python 测试扫描 + latent command 机制简单可靠）
- 但 Python 侧的 `automation_test` 工具库功能有限，没有 unittest/unittest.mock 集成
- **建议**: 可以放心使用核心功能（test_*.py 自动发现 + latent command），但不要期待新特性。如需更完善的 Python 测试能力，考虑自行扩展 `automation_test` 工具库

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/PythonAutomationTest)
- [C++ 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Tests/PythonAutomationTest/Source/PythonAutomationTest/Private/PythonAutomationTest.cpp)
- [Python 测试工具库](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Tests/PythonAutomationTest/Content/Python/automation_test/unittest_utilities.py)
- [AutomationScheduler 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Tests/PythonAutomationTest/Content/Python/unreal_pythonautomationtest.py)
