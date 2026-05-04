# Database Support

> Abstract Database Support

| 属性 | 值 |
|---|---|
| 分类 | Database |
| 默认启用 | ❌ 否（需手动启用） |
| 隐藏 | 是（Hidden: true） |
| 包含内容 | 否 |
| 模块 | DatabaseSupport (Runtime) |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（~7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/DatabaseSupport) | |

## 用途

DatabaseSupport 是 UE5 数据库抽象层的**接口定义插件**。它本身不实现任何数据库功能，而是定义了一组纯虚基类（`FDataBaseConnection`、`FDataBaseRecordSet`），供其他插件（如 SQLiteSupport、ADOSupport、RemoteDatabaseSupport）继承和实现。

这个插件存在的意义是：让 UE 的数据库相关代码可以针对抽象接口编程，而不依赖于具体的数据库实现。你可以编写使用 `FDataBaseConnection` 的代码，然后在运行时（或打包时）决定使用 SQLite、ADO 还是远程数据库代理。

> **注意**：该插件标记为 `Hidden: true` 且 `EnabledByDefault: false`，属于底层基础设施插件，不在编辑器的插件浏览器中显示。它通常作为其他数据库插件的依赖被自动加载。

## 使用场景

- 你需要一个统一的数据库访问接口，不想在代码中硬绑定到 SQLite 或其他具体数据库 → 用 DatabaseSupport 定义的抽象接口
- 你要实现自定义数据库后端（如 MySQL、PostgreSQL 等 UE 官方不支持的数据库）→ 继承 `FDataBaseConnection` 和 `FDataBaseRecordSet`
- 你已经在使用 SQLiteSupport 或 ADOSupport → 它们已经在底层依赖了本插件

## 蓝图用法

本插件**没有暴露任何蓝图接口**。所有类均为纯 C++ 抽象基类，没有 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。

如果需要在蓝图中操作数据库，请使用具体的数据库插件（如 SQLiteSupport）提供的蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "Database.h"        // 核心抽象类
#include "DatabaseSupport.h" // 模块接口
```

### 核心类

#### `EDataBaseUnrealTypes` — 数据类型枚举

```cpp
enum EDataBaseUnrealTypes
{
    DBT_UNKOWN,   // 未知类型
    DBT_FLOAT,    // 浮点数
    DBT_INT,      // 整数
    DBT_STRING,   // 字符串
};
```

#### `FDatabaseColumnInfo` — 列信息

描述数据库记录集中某一列的元信息：

```cpp
struct FDatabaseColumnInfo
{
    FString ColumnName;            // 列名
    EDataBaseUnrealTypes DataType; // 数据类型
};
```

#### `FDataBaseRecordSet` — 记录集（抽象基类）

对应 SQL 查询返回的结果集，提供行级数据访问接口：

```cpp
class FDataBaseRecordSet
{
public:
    virtual int32 GetRecordCount() const;                          // 记录总数
    virtual FString GetString(const TCHAR* Column) const;          // 获取字符串值
    virtual int32 GetInt(const TCHAR* Column) const;               // 获取整数值
    virtual float GetFloat(const TCHAR* Column) const;             // 获取浮点值
    virtual int64 GetBigInt(const TCHAR* Column) const;            // 获取 int64 值
    virtual TArray<FDatabaseColumnInfo> GetColumnNames() const;    // 获取所有列信息

protected:
    virtual void MoveToFirst();    // 移动到第一条记录
    virtual void MoveToNext();     // 移动到下一条记录
    virtual bool IsAtEnd() const;  // 是否到达末尾
};
```

内置 `TIterator` 迭代器，支持范围 for 风格遍历：

```cpp
FDataBaseRecordSet* ResultSet = /* ... */;
for (FDataBaseRecordSet::TIterator It(ResultSet); It; ++It)
{
    FString Name = It->GetString(TEXT("Name"));
    int32 Score = It->GetInt(TEXT("Score"));
}
```

#### `FDataBaseConnection` — 数据库连接（抽象基类）

对应一个数据库连接，提供打开、关闭、执行命令等接口：

```cpp
class FDataBaseConnection
{
public:
    // 打开连接。ConnectionString 语义取决于具体实现
    virtual bool Open(const TCHAR* ConnectionString,
                      const TCHAR* RemoteConnectionIP,
                      const TCHAR* RemoteConnectionStringOverride);

    // 关闭连接
    virtual void Close();

    // 执行不返回结果集的命令（INSERT/UPDATE/DELETE 等）
    virtual bool Execute(const TCHAR* CommandString);

    // 执行返回结果集的命令（SELECT 等），调用方负责删除 RecordSet
    virtual bool Execute(const TCHAR* CommandString, FDataBaseRecordSet*& RecordSet);
};
```

### 基本用法

通过具体实现插件使用数据库连接（以 SQLite 为例）：

```cpp
#include "SQLiteDatabaseConnection.h"

// 创建连接
FSQLiteDatabaseConnection Connection;

// 打开数据库文件
if (Connection.Open(TEXT("MyDatabase.db"), nullptr, nullptr))
{
    // 执行查询
    FDataBaseRecordSet* ResultSet = nullptr;
    if (Connection.Execute(TEXT("SELECT * FROM Players"), ResultSet))
    {
        // 遍历结果
        for (FDataBaseRecordSet::TIterator It(ResultSet); It; ++It)
        {
            FString Name = It->GetString(TEXT("Name"));
            int32 Level = It->GetInt(TEXT("Level"));
        }

        // 调用方负责释放
        delete ResultSet;
    }

    // 关闭连接
    Connection.Close();
}
```

### 进阶用法 — 实现自定义数据库后端

如果你需要接入 UE 不原生支持的数据库，可以继承这两个基类：

```cpp
// MyDatabaseConnection.h
#pragma once
#include "Database.h"

class FMyDatabaseConnection : public FDataBaseConnection
{
public:
    virtual bool Open(const TCHAR* ConnectionString,
                      const TCHAR* RemoteConnectionIP,
                      const TCHAR* RemoteConnectionStringOverride) override;
    virtual void Close() override;
    virtual bool Execute(const TCHAR* CommandString) override;
    virtual bool Execute(const TCHAR* CommandString, FDataBaseRecordSet*& RecordSet) override;

private:
    // 你的数据库原生句柄
    void* NativeHandle = nullptr;
};

// MyDatabaseResultSet.h
class FMyDatabaseResultSet : public FDataBaseRecordSet
{
public:
    virtual int32 GetRecordCount() const override;
    virtual FString GetString(const TCHAR* Column) const override;
    virtual int32 GetInt(const TCHAR* Column) const override;
    virtual float GetFloat(const TCHAR* Column) const override;

protected:
    virtual void MoveToFirst() override;
    virtual void MoveToNext() override;
    virtual bool IsAtEnd() const override;

private:
    // 你的结果集数据
    int32 CurrentIndex = 0;
    // ...
};
```

## Demo 示例

```cpp
// MyGame.Build.cs — 添加依赖
PublicDependencyModuleNames.AddRange(new string[] { "DatabaseSupport", "SQLiteSupport" });
```

```cpp
// MyDatabaseHelper.h
#pragma once
#include "Database.h"

class FMyDatabaseHelper
{
public:
    static void QueryPlayers(FDataBaseConnection& Connection)
    {
        FDataBaseRecordSet* ResultSet = nullptr;
        if (Connection.Execute(TEXT("SELECT Name, Level FROM Players"), ResultSet))
        {
            for (FDataBaseRecordSet::TIterator It(ResultSet); It; ++It)
            {
                UE_LOG(LogTemp, Log, TEXT("Player: %s, Level: %d"),
                    *It->GetString(TEXT("Name")),
                    It->GetInt(TEXT("Level")));
            }
            delete ResultSet;
        }
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块（FString、TArray 等基础类型） |

使用者无需额外依赖——DatabaseSupport 本身只依赖 Core，但实际使用数据库功能时需要额外依赖具体的数据库插件（见下方"相关插件"）。

## 生态插件

DatabaseSupport 是 UE 数据库抽象层的基础，以下插件实现了其接口：

| 插件 | 说明 |
|---|---|
| `SQLiteSupport` | SQLite 数据库实现，适合本地存储 |
| `ADOSupport` | Windows ADO 数据库访问，适合连接 SQL Server 等 |
| `RemoteDatabaseSupport` | 通过 Socket 连接远程数据库代理，适合不支持原生数据库的平台 |

## 维护状态

### 近期更新

| 日期 | Hash | 提交说明 | 解读 |
|---|---|---|---|
| 2025-06-13 | `185bf170` | Replace some usages of FORCEINLINE with inline in Engine modules | 全引擎范围的代码风格统一，非功能性改动 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol | 元数据更新（HTTPS 链接），无功能变化 |
| 2019-12-27 | `360d078c` | Second batch of remaining Engine copyright updates | 版权声明更新，无功能变化 |

### 维护评价

- **创建时间**：2019 年 1 月（~7 年前）
- **功能层面从未更新过**：自创建以来没有任何功能性代码改动，所有 commit 都是版权更新、链接修复或代码风格统一
- **状态**：接口稳定，基本处于"已完成"状态。作为一个纯抽象接口层，这种稳定性是合理的
- **隐藏且默认关闭**：属于底层基础设施，不建议直接启用，通常由 SQLiteSupport 等插件自动依赖
- **推荐度**：如果你需要自定义数据库后端，这是必须依赖的基础模块。对于一般用户，直接使用 SQLiteSupport 即可，无需直接接触本插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/DatabaseSupport)
- [SQLiteSupport](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/SQLiteSupport) — SQLite 实现
- [ADOSupport](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/ADOSupport) — ADO 实现
- [RemoteDatabaseSupport](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/RemoteDatabaseSupport) — 远程数据库实现
