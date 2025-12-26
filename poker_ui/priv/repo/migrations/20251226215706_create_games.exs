defmodule PokerUi.Repo.Migrations.CreateGames do
  use Ecto.Migration

  def change do
    create table(:games, primary_key: false) do
      add :id, :binary_id, primary_key: true
      add :title, :string
      add :pot, :integer

      timestamps(type: :utc_datetime)
    end
  end
end
