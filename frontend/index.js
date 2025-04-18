document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("file1");
  const analyzeBtn = document.querySelector(".analyze-btn");
  const recommendationBlock = document.getElementById("recommendation-block");

  fileInput.addEventListener("change", (e) => {
    const fileName = e.target.files[0]?.name || "Файл не выбран";
    document.getElementById("file1-name").textContent = fileName;
  });

  analyzeBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];
    if (!file) return alert("Пожалуйста, выберите файл резюме!");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const uploadResponse = await fetch(
        "http://localhost:8000/upload-resume/",
        {
          method: "POST",
          body: formData,
        }
      );
      if (!uploadResponse.ok) {
        const errorText = await uploadResponse.text();
        throw new Error(
          `Ошибка загрузки: ${uploadResponse.status} - ${errorText}`
        );
      }
      const uploadData = await uploadResponse.json();

      const recommendationsResponse = await fetch(
        `http://localhost:8000/get-recommendations/${uploadData.candidate.id}`
      );
      if (!recommendationsResponse.ok) {
        const errorText = await recommendationsResponse.text();
        throw new Error(
          `Ошибка получения рекомендаций: ${recommendationsResponse.status} - ${errorText}`
        );
      }
      const recommendationsData = await recommendationsResponse.json();

      recommendationBlock.innerHTML = "";
      recommendationBlock.style.display = "block";

      const candidateHTML = `
                <div class="candidate-header">
                    <h3>${uploadData.candidate.full_name}</h3>
                </div>
            `;
      recommendationBlock.insertAdjacentHTML("beforeend", candidateHTML);

      const hardSkills = uploadData.candidate.hard_skills;
      if (Object.keys(hardSkills).length > 0) {
        const hardSkillsHTML = `
                    <div class="hard-skills-container">
                        ${Object.entries(hardSkills)
                          .map(
                            ([skill, level]) => `
                            <div class="skill-square level-${level}">
                                <div>${skill}</div>
                                <div class="skill-level">${level}</div>
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                `;
        recommendationBlock.insertAdjacentHTML("beforeend", hardSkillsHTML);
      }

      recommendationsData.roles.forEach((role, index) => {
        const skillsToImprove = Object.entries(role.skills)
          .filter(
            ([skill, req]) =>
              req > (uploadData.candidate.hard_skills[skill] || 0)
          )
          .sort((a, b) => {
            const gapA = a[1] - (uploadData.candidate.hard_skills[a[0]] || 0);
            const gapB = b[1] - (uploadData.candidate.hard_skills[b[0]] || 0);
            const userLevelA = uploadData.candidate.hard_skills[a[0]] || 0;
            const userLevelB = uploadData.candidate.hard_skills[b[0]] || 0;
            if (userLevelA === 0 && userLevelB !== 0) return -1;
            if (userLevelB === 0 && userLevelA !== 0) return 1;
            return gapB - gapA;
          });

        const getGapColor = (gap) => {
          if (gap === 0) return "green";
          if (gap === 1) return "#FFC107";
          return "red";
        };

        const getLevelLabel = (level) => {
          switch (level) {
            case 1:
              return "Базовый";
            case 2:
              return "Средний";
            case 3:
              return "Продвинутый";
            default:
              return "Отсутствует";
          }
        };

        const strongSkills = Object.entries(uploadData.candidate.hard_skills)
          .filter(
            ([skill, level]) => role.skills[skill] && level > role.skills[skill]
          )
          .map(
            ([skill, level]) =>
              `<li>${skill} (уровень ${level} - ${getLevelLabel(
                level
              )}, требуется ${role.skills[skill]})</li>`
          )
          .join("");

        const additionalSkills = Object.entries(
          uploadData.candidate.hard_skills
        )
          .filter(
            ([skill, level]) => !role.skills[skill] || role.skills[skill] === 0
          )
          .map(
            ([skill, level]) =>
              `<li>${skill} (уровень ${level} - ${getLevelLabel(level)})</li>`
          )
          .join("");

        const roleHTML = `
                    <div class="role-block ${
                      index === 0 ? "highlighted-role" : ""
                    }">
                        <div class="role-header">
                            <h4>${
                              index === 0
                                ? "Наиболее подходящая профессия: "
                                : "Другие профессии: "
                            }${role.name}</h4>
                            <span class="match-percent">${
                              role.match_percent
                            }% совпадение</span>
                        </div>
                        <div class="skills-table-container" style="max-height: 300px; overflow-y: auto;">
                            <table class="skills-table">
                                <thead>
                                    <tr>
                                        <th>Недостающий навык</th>
                                        <th>Уровень кандидата</th>
                                        <th>Требуемый уровень</th>
                                        <th>Разрыв</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${
                                      skillsToImprove.length > 0
                                        ? skillsToImprove
                                            .map(([skill, req]) => {
                                              const userLevel =
                                                uploadData.candidate
                                                  .hard_skills[skill] || 0;
                                              const gap =
                                                req > 0
                                                  ? Math.max(req - userLevel, 0)
                                                  : 0;
                                              const color = getGapColor(gap);
                                              return `
                                                <tr>
                                                    <td>${skill}</td>
                                                    <td>${userLevel}</td>
                                                    <td>${req}</td>
                                                    <td style="color: ${color};">${gap}</td>
                                                </tr>
                                            `;
                                            })
                                            .join("")
                                        : '<tr><td colspan="4">Все требуемые навыки соответствуют или превосходят требования</td></tr>'
                                    }
                                </tbody>
                            </table>
                        </div>
                        ${
                          strongSkills.length > 0
                            ? `
                            <div class="strong-skills">
                                <h5>Сильные стороны:</h5>
                                <ul>${strongSkills}</ul>
                            </div>
                        `
                            : ""
                        }
                        ${
                          additionalSkills.length > 0
                            ? `
                            <div class="additional-skills">
                                <h5>Дополнительные навыки:</h5>
                                <ul>${additionalSkills}</ul>
                            </div>
                        `
                            : ""
                        }
                    </div>
                `;
        recommendationBlock.insertAdjacentHTML("beforeend", roleHTML);
      });

      if (recommendationsData.soft_skills?.length > 0) {
        const softSkillsHTML = `
                    <div class="soft-skills">
                        <h4>Soft skills:</h4>
                        <ul>
                            ${recommendationsData.soft_skills
                              .map((skill) => `<li>${skill}</li>`)
                              .join("")}
                        </ul>
                    </div>
                `;
        recommendationBlock.insertAdjacentHTML("beforeend", softSkillsHTML);
      }
    } catch (error) {
      console.error("Ошибка:", error);
      alert(`Ошибка: ${error.message}`);
    }
  });
});
