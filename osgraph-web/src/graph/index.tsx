/** @jsxImportSource @emotion/react */
import { css } from "@emotion/react";
import { useTranslation } from "react-i18next";

export default () => {
  const { t } = useTranslation();
  return (
    <div>
      <a href="/">Back</a>
      <h1
        css={css`
          font-size: 48px;
        `}
      >
        {t("graph")}
      </h1>
    </div>
  );
};
